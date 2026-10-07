# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Cohen, Nussenbaum, Dorfman, Gershman &
Hartley (2020), "The rational use of causal inference to guide reinforcement
learning strengthens with age", npj Science of Learning, against any dataset in
the Psych-301 unified schema (see schema.md).

Effects tested:
- attribution_causal_alignment (exp0): in the Robber territory participants
  attribute negative outcomes (rocks) to the hidden agent more than positive
  outcomes, and in the Millionaire territory they attribute positive outcomes
  (gold) more than negative outcomes — a reward-outcome by territory interaction
  on attribution (latent_guess).
- learning_over_trials (exp0): participants learn to select the better (optimal)
  mine more frequently as each 50-trial block progresses (main effect of trial on
  optimal choice).
- age_optimal_choice (exp0): older participants select the better mine on a
  higher proportion of trials than younger participants (main effect of age on
  optimal choice).
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

EXPERIMENTS = ["exp0"]
VALID = 1


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD — `cd` into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      exp0: participant_id, trial, response (and: block, condition, feedback,
            latent_guess, optimal_choice, valid, age)
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _valid_jr(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["valid"] == VALID]


def check_attribution_causal_alignment(data: dict[str, pd.DataFrame]) -> dict:
    """"Consistent with the experimental manipulation, there was a significant
    reward outcome by territory interaction (chi2(2, N = 90) = 87.69, p < 0.0001)
    indicating that participants attributed negative outcomes most often to the
    Robber ... while attributing positive outcomes most often to the Millionaire"
    — Cohen et al. 2020, p.2, Results/Behavioral analyses."""
    df = _valid_jr(data["exp0"])
    cond = df["condition"]
    fb = df["feedback"]
    at = df["latent_guess"]

    robber = cond == "robber"
    millionaire = cond == "millionaire"
    rocks = fb == 0
    gold = fb == 1

    robber_rocks_attr = at[robber & rocks].mean()
    robber_gold_attr = at[robber & gold].mean()
    millionaire_rocks_attr = at[millionaire & rocks].mean()
    millionaire_gold_attr = at[millionaire & gold].mean()

    robber_win = robber_rocks_attr > robber_gold_attr
    millionaire_win = millionaire_gold_attr > millionaire_rocks_attr

    ct_robber = pd.crosstab(fb[robber], at[robber])
    ct_millionaire = pd.crosstab(fb[millionaire], at[millionaire])
    chi_r, p_r, _, _ = stats.chi2_contingency(ct_robber)
    chi_m, p_m, _, _ = stats.chi2_contingency(ct_millionaire)

    effect_size = (robber_rocks_attr - robber_gold_attr) + (millionaire_gold_attr - millionaire_rocks_attr)
    reproduced = bool(robber_win and millionaire_win and p_r < 0.05 and p_m < 0.05)
    return {
        "effect_name": "attribution_causal_alignment",
        "experiment": "exp0",
        "original_effect_size": 87.69,  # chi2(2) reward x territory interaction
        "effect_size": float(effect_size),
        "reproduced": reproduced,
        "robber_rocks_attr": float(robber_rocks_attr),
        "robber_gold_attr": float(robber_gold_attr),
        "millionaire_rocks_attr": float(millionaire_rocks_attr),
        "millionaire_gold_attr": float(millionaire_gold_attr),
        "robber_p": float(p_r),
        "millionaire_p": float(p_m),
    }


def check_learning_over_trials(data: dict[str, pd.DataFrame]) -> dict:
    """"We found significant main effects of trial number (chi2(1, N = 90) =
    100.46, p < 0.0001) ... indicating that participants learned to select the
    more highly rewarded mine more frequently as each block progressed"
    — Cohen et al. 2020, p.3, Results/Behavioral analyses."""
    df = _valid_jr(data["exp0"])
    df = df.copy()
    df["trial_in_block"] = df["trial"] % 50
    X = sm.add_constant(df["trial_in_block"])
    model = sm.Logit(df["optimal_choice"], X).fit(disp=0)
    coef = float(model.params["trial_in_block"])
    p = float(model.pvalues["trial_in_block"])
    reproduced = bool(coef > 0 and p < 0.05)
    return {
        "effect_name": "learning_over_trials",
        "experiment": "exp0",
        "original_effect_size": 100.46,  # chi2(1) main effect of trial
        "effect_size": coef,
        "reproduced": reproduced,
        "p": p,
    }


def check_age_optimal_choice(data: dict[str, pd.DataFrame]) -> dict:
    """"[M]ain effects of ... age (chi2(1, N = 90) = 13.97, p < 0.001) ...
    indicating that ... older participants selected the better mine on a higher
    proportion of trials" — Cohen et al. 2020, p.3, Results/Behavioral analyses."""
    df = _valid_jr(data["exp0"])
    per = df.groupby("participant_id").agg(age=("age", "mean"), opt=("optimal_choice", "mean"))
    r, p = stats.pearsonr(per["age"], per["opt"])
    reproduced = bool(r > 0 and p < 0.05)
    return {
        "effect_name": "age_optimal_choice",
        "experiment": "exp0",
        "original_effect_size": 13.97,  # chi2(1) main effect of age
        "effect_size": float(r),
        "reproduced": reproduced,
        "p": float(p),
    }


EFFECTS = [
    check_attribution_causal_alignment,
    check_learning_over_trials,
    check_age_optimal_choice,
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
