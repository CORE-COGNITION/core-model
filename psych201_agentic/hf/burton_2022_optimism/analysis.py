# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Burton, Harris, Shah, & Hahn (2022),
"Optimism Where There is None: Asymmetric Belief Updating Observed with
Valence-Neutral Life Events", against any dataset in the Psych-301 unified schema
(see schema.md).

Effects tested:
- asymmetric_belief_updating_neutral_exp0 (exp0): among trials rated valence-neutral,
  the magnitude of belief updating |E2-E1| is greater when the direction of error is
  downwards (BR < E1) than upwards (BR > E1). Tested with a linear mixed-effects model
  (update ~ direction of error, random intercept by participant), as in the paper's
  pre-registered main analysis.
- asymmetric_belief_updating_neutral_exp1 (exp1): same as above for Study 2.
- asymmetric_belief_updating_neutral_exp2 (exp2): same as above for Study 3.
"""
from __future__ import annotations

import argparse
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

EXPERIMENTS = ["exp0", "exp1", "exp2"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD — `cd` into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      exp0/exp1/exp2: participant_id, block, phase, E1, E2, BR, Valence
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _neutral_asymmetry(df: pd.DataFrame) -> tuple[float, float, int, int]:
    """Run the paper's main analysis on one study's data.

    Returns (coefficient for upwards vs downwards direction of error, p-value,
    n neutral trials, n participants) for trials whose event was rated
    valence-neutral (Valence == 3).
    """
    ev = df[df["phase"] == "e1"][["participant_id", "block", "E1", "BR", "E2", "Valence"]].copy()
    ev["update"] = (ev["E2"] - ev["E1"]).abs()
    ev["upwards"] = (ev["BR"] > ev["E1"]).astype(int)
    neut = ev[ev["Valence"] == 3]
    model = smf.mixedlm("update ~ upwards", neut, groups=neut["participant_id"]).fit()
    coef = float(model.params["upwards"])
    p = float(model.pvalues["upwards"])
    return coef, p, len(neut), neut["participant_id"].nunique()


def check_asymmetric_belief_updating_neutral_exp0(data: dict[str, pd.DataFrame]) -> dict:
    """"In all three studies, asymmetric belief updating was observed with neutral life
    events (Fig. 2)." ... "an upwards direction of error (i.e., BR > E1) decreased update
    scores by approximately 9.13 percentage points ... as compared to downwards direction
    of error." — Burton et al. (2022), p.9, Results/Main Analysis."""
    coef, p, n, nsub = _neutral_asymmetry(data["exp0"])
    reproduced = bool(coef < 0 and p < 0.05)
    return {
        "effect_name": "asymmetric_belief_updating_neutral_exp0",
        "experiment": "exp0",
        "original_effect_size": -9.13,
        "effect_size": coef,
        "reproduced": reproduced,
        "p": p,
        "n_neutral_trials": n,
        "n_participants": nsub,
    }


def check_asymmetric_belief_updating_neutral_exp1(data: dict[str, pd.DataFrame]) -> dict:
    """"In Study 2 ... an upwards direction of error (i.e., BR > E1) decreased update
    scores by about 6.24 percentage points (fixed effect estimate) ± 0.71 (standard
    error), as compared to downwards direction of error." — Burton et al. (2022), p.10,
    Results/Main Analysis."""
    coef, p, n, nsub = _neutral_asymmetry(data["exp1"])
    reproduced = bool(coef < 0 and p < 0.05)
    return {
        "effect_name": "asymmetric_belief_updating_neutral_exp1",
        "experiment": "exp1",
        "original_effect_size": -6.24,
        "effect_size": coef,
        "reproduced": reproduced,
        "p": p,
        "n_neutral_trials": n,
        "n_participants": nsub,
    }


def check_asymmetric_belief_updating_neutral_exp2(data: dict[str, pd.DataFrame]) -> dict:
    """"In Study 3 ... an upwards direction of error (i.e., BR > E1) decreased update
    scores by about 6.51 percentage points (fixed effect estimate) ± 0.79 (standard
    error) as compared to downwards direction of error." — Burton et al. (2022), p.10,
    Results/Main Analysis."""
    coef, p, n, nsub = _neutral_asymmetry(data["exp2"])
    reproduced = bool(coef < 0 and p < 0.05)
    return {
        "effect_name": "asymmetric_belief_updating_neutral_exp2",
        "experiment": "exp2",
        "original_effect_size": -6.51,
        "effect_size": coef,
        "reproduced": reproduced,
        "p": p,
        "n_neutral_trials": n,
        "n_participants": nsub,
    }


EFFECTS = [
    check_asymmetric_belief_updating_neutral_exp0,
    check_asymmetric_belief_updating_neutral_exp1,
    check_asymmetric_belief_updating_neutral_exp2,
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
    print(f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  {'p':>8}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{r['p']:>8.4f}  {'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()
