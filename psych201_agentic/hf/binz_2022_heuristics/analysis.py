# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Binz, Gershman, Schulz & Endres (2022),
"Heuristics from bounded meta-learned inference", against any dataset in the
Psych-301 unified schema (see schema.md).

Effects tested:
- above_chance_accuracy (exp0, exp1, exp2): in the ranked, directional and
  2-feature-unknown inferential paired-comparison tasks, participants choose the
  better option more than chance (paper: 68.25%, 73.85%, 71.59%); one-sample
  t-test of per-participant accuracy against 0.5, expected positive and p<.05.
- learning_over_trials (exp0, exp1, exp2): accuracy increases over trials within
  a task (mixed-effects logistic regression fixed effect of trial, β>0, p<.001);
  here a binomial-logit coefficient of trial, expected positive and p<.05.
- four_feature_unknown_no_learning (exp3): in the harder 4-feature, unknown
  ranking/direction task, performance does not improve over trials
  (paper: β=-0.01, n.s.); logit coefficient of trial expected non-significant.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

EXPERIMENTS = ["exp0", "exp1", "exp2", "exp3"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD.

    Required columns per experiment: participant_id, task_id, trial, response,
    target, correct.
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _trial_logit(df: pd.DataFrame):
    """Partial pooling logit of correct on trial (trials reset within each task)."""
    X = sm.add_constant(df["trial"])
    m = sm.GLM(df["correct"], X, family=sm.families.Binomial()).fit()
    return float(m.params["trial"]), float(m.pvalues["trial"])


def check_above_chance_accuracy(data: dict[str, pd.DataFrame]) -> dict:
    """\"On average, participants made 68.25±7.55% correct choices\" ...; \"all
    participants chose the better option more frequently than ... chance level
    performance\" — Binz et al. 2022, p.37-44, Results/Performance (Exp 1,2 & 3)."""
    exps = ["exp0", "exp1", "exp2"]
    accs = np.concatenate([data[e].groupby("participant_id").correct.mean().values
                           for e in exps])
    t, p = stats.ttest_1samp(accs, 0.5)
    mean = float(accs.mean())
    reproduced = bool(mean > 0.5 and p < 0.05)
    return {
        "effect_name": "above_chance_accuracy",
        "experiment": "exp0,exp1,exp2",
        "original_effect_size": 0.712,  # avg of 68.25%, 73.85%, 71.59% in paper
        "effect_size": mean,
        "p": float(p),
        "reproduced": reproduced,
    }


def check_learning_over_trials(data: dict[str, pd.DataFrame]) -> dict:
    """\"a significant fixed effect of trial number ... onto choosing the better
    option\" — Binz et al. 2022, p.38-48, Results/Performance (Exp 1,2 & 3)."""
    exps = ["exp0", "exp1", "exp2"]
    coefs = [_trial_logit(data[e]) for e in exps]
    mean_beta = float(np.mean([c for c, _ in coefs]))
    reproduced = all(beta > 0 and p < 0.05 for beta, p in coefs)
    return {
        "effect_name": "learning_over_trials",
        "experiment": "exp0,exp1,exp2",
        "original_effect_size": 0.133,  # avg of β=0.12, 0.08, 0.20 in paper
        "effect_size": mean_beta,
        "coefs": coefs,
        "reproduced": reproduced,
    }


def check_four_feature_unknown_no_learning(data: dict[str, pd.DataFrame]) -> dict:
    """\"The results ... showed no significant fixed effect of either trial number
    (β=-0.01, p=.79)...\" — Binz et al. 2022, p.91, Appendix G (Exp 3b)."""
    beta, p = _trial_logit(data["exp3"])
    reproduced = bool(p >= 0.05 and beta <= 0.05)
    return {
        "effect_name": "four_feature_unknown_no_learning",
        "experiment": "exp3",
        "original_effect_size": -0.01,  # paper β for trial
        "effect_size": beta,
        "p": float(p),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_above_chance_accuracy,
    check_learning_over_trials,
    check_four_feature_unknown_no_learning,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. No printing."""
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None,
                        help=f"CSV path for {exp}; defaults to ./{exp}.csv in CWD")
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS
               if getattr(args, exp)}
    for exp in EXPERIMENTS:
        if exp in sources:
            print(f"{exp}: {sources[exp]}")
        else:
            print(f"{exp}: (default — local ./{exp}.csv)")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<12}  {'orig':>8}  {'this':>8}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<12}  "
              f"{r['original_effect_size']:>8.3f}  {r['effect_size']:>8.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()
