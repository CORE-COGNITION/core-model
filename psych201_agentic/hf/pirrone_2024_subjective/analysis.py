# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Pirrone (2024), "Subjective utility
modulates the effect of overall stimulus intensity on decision-making"
(Unpublished manuscript, OSF) against any dataset in the Psych-301 unified schema
(see schema.md).

The source PDF is a constructed 2-page document (OSF README + metadata) with no
full manuscript text, so primary effects are derived from the title and the
derived columns present in the CSV. No numeric effect sizes are reported, so
"original_effect_size" is NaN and reproduction rests on significance + sign.

Effects tested:
- magnitude_effect_on_rt (exp0): overall stimulus intensity (magnitude) affects
  decision speed; OLS rt ~ magnitude. Reproduced if the coefficient is
  significant (p < .05). Direction is not specified in the 2-page source; the
  observed coefficient is positive (higher magnitude -> slower RT).
- utility_modulates_magnitude_rt (exp0): subjective utility (nonlinear_preference)
  modulates the effect of overall stimulus intensity on decision-making (the
  headline claim); OLS rt ~ magnitude*nonlinear_preference. Reproduced if the
  interaction term is significant (p < .05).
- variance_preference_magnitude (exp0): participants more often choose the
  higher-variance lottery when magnitude is high (utility of variance);
  OLS prefer_variance ~ magnitude. Reproduced if the coefficient is positive
  and significant (p < .05).
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

EXPERIMENTS = ["exp0"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD.

    Required columns per experiment:
      exp0: participant_id, trial, response, rt, magnitude, nonlinear_preference,
            prefer_variance
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def check_magnitude_effect_on_rt(data: dict[str, pd.DataFrame]) -> dict:
    """"Whether subjective utility modulates the effect of overall stimulus
    intensity on decision-making ... with reaction time as the dependent
    measure." — Pirrone 2024, title/README (no page/section: constructed PDF).
    Overall stimulus intensity (magnitude) has a significant effect on RT.
    Direction is not stated in the source; any significant effect reproduces.
    """
    df = data["exp0"]
    fit = smf.ols("rt ~ magnitude", data=df).fit()
    beta = float(fit.params["magnitude"])
    p = float(fit.pvalues["magnitude"])
    return {
        "effect_name": "magnitude_effect_on_rt",
        "experiment": "exp0",
        "original_effect_size": float("nan"),
        "effect_size": beta,
        "p_value": p,
        "reproduced": bool(p < 0.05),
    }


def check_utility_modulates_magnitude_rt(data: dict[str, pd.DataFrame]) -> dict:
    """"Subjective utility modulates the effect of overall stimulus intensity on
    decision-making" — Pirrone 2024, title. Subjective-utility proxy
    (nonlinear_preference, constant within participant) moderates the effect of
    magnitude on RT: the magnitude x nonlinear_preference interaction in
    rt ~ magnitude * nonlinear_preference is significant.
    """
    df = data["exp0"]
    fit = smf.ols("rt ~ magnitude * nonlinear_preference", data=df).fit()
    beta = float(fit.params["magnitude:nonlinear_preference"])
    p = float(fit.pvalues["magnitude:nonlinear_preference"])
    return {
        "effect_name": "utility_modulates_magnitude_rt",
        "experiment": "exp0",
        "original_effect_size": float("nan"),
        "effect_size": beta,
        "p_value": p,
        "reproduced": bool(p < 0.05),
    }


def check_variance_preference_magnitude(data: dict[str, pd.DataFrame]) -> dict:
    """"Lottery variance ... prefer_variance (whether the participant chose the
    higher-variance lottery)" — Pirrone 2024, data description. Choosing the
    higher-variance lottery is more likely when overall magnitude is high
    (utility of variance): coefficient of magnitude in
    prefer_variance ~ magnitude is positive and significant.
    """
    df = data["exp0"]
    fit = smf.ols("prefer_variance ~ magnitude", data=df).fit()
    beta = float(fit.params["magnitude"])
    p = float(fit.pvalues["magnitude"])
    reproduced = bool(beta > 0 and p < 0.05)
    return {
        "effect_name": "variance_preference_magnitude",
        "experiment": "exp0",
        "original_effect_size": float("nan"),
        "effect_size": beta,
        "p_value": p,
        "reproduced": reproduced,
    }


EFFECTS = [
    check_magnitude_effect_on_rt,
    check_utility_modulates_magnitude_rt,
    check_variance_preference_magnitude,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. No printing — pure return."""
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
    print(f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  {'p':>9}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
              f"{np.nan if r['original_effect_size'] is np.nan else r['original_effect_size']:>10}  "
              f"{r['effect_size']:>10.4f}  {r['p_value']:>9.3e}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()
