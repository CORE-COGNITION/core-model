# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "statsmodels", "scipy"]
# ///
"""Check the primary behavioral effects of Ciranka & van den Bos (2025), "Internal
uncertainty impacts social information use in risky choice across adolescence"
(Communications Psychology) against any dataset in the Psych-301 unified schema
(see schema.md).

This paper is a single laboratory 'Developing Marbles' lottery experiment
(exp0): 166 participants aged 10-26 each made risky choices (safe vs risky jar)
under a within-subject external-uncertainty manipulation (from_description vs
from_experience) and a social-information manipulation (peer chose risky / peer
chose safe / solo). Only behavioral effects derivable from the CSV are tested —
the paper's headline claim (internal-uncertainty model) is a model fit, not a
behavioral effect, so it is out of scope here.

Effects tested:
- expected_value_risky_choice (exp0): risky-jar choice propensity increases with
  the risky option's expected value (sanity-check main effect; b_EV > 0). Tested
  as logistic regression of risky choice on EV.
- social_risky_influence (exp0): participants choose the risky jar more often when
  social information indicates the peer chose the risky jar than when they have no
  (or safe) social information (b_socialrisk > 0). Tested as risky-choice rate
  comparison peer-risky vs not-peer-risky.
- risky_choice_age_decline (exp0): risky-choice propensity declines with age
  (negative linear age trend, b_age < 0). Tested as logistic regression of risky
  choice on age.
"""
from __future__ import annotations

import argparse
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

EXPERIMENTS = ["exp0"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD.

    Required columns per experiment:
      exp0: participant_id, trial, block, response, response_type, condition,
            phase, age, valueGamble, probGamble, valueSure, OtherChoseRisk
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _choice_df(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return data["exp0"].query("response_type == 'choice'").copy()


def check_expected_value_risky_choice(data: dict[str, pd.DataFrame]) -> dict:
    """"We predicted risky decisions on each trial using predictors... Overall,
    participants chose the risky jar more often when the expected value [was
    higher] (b_EV=4.11, 95% CI=[3.98, 4.24], BF10>100)" — Ciranka & van den Bos,
    2025, p.7, Results/Behavioural analyses."""
    df = _choice_df(data)
    df["EV"] = df["probGamble"] * df["valueGamble"] - df["valueSure"]
    model = smf.logit("response ~ EV", data=df).fit(disp=0)
    effect_size = float(model.params["EV"])
    reproduced = bool(model.params["EV"] > 0 and model.pvalues["EV"] < 0.05)
    return {
        "effect_name": "expected_value_risky_choice",
        "experiment": "exp0",
        "original_effect_size": 4.11,
        "effect_size": effect_size,
        "reproduced": reproduced,
    }


def check_social_risky_influence(data: dict[str, pd.DataFrame]) -> dict:
    """"Participants chose the risky jar more often when social information
    favoured the risky jar (b_socialrisk=0.27, 95% CI=[0.16, 0.37], BF10>100)"
    — Ciranka & van den Bos, 2025, p.7, Results/Behavioural analyses."""
    df = _choice_df(data)
    df["peer_risky"] = (df["OtherChoseRisk"] == 1).astype(int)
    model = smf.logit("response ~ C(peer_risky)", data=df).fit(disp=0)
    effect_size = float(model.params["C(peer_risky)[T.1]"])
    rate_risky = df.loc[df["peer_risky"] == 1, "response"].mean()
    rate_other = df.loc[df["peer_risky"] == 0, "response"].mean()
    reproduced = bool(rate_risky > rate_other and model.pvalues["C(peer_risky)[T.1]"] < 0.05)
    return {
        "effect_name": "social_risky_influence",
        "experiment": "exp0",
        "original_effect_size": 0.27,
        "effect_size": effect_size,
        "reproduced": reproduced,
    }


def check_risky_choice_age_decline(data: dict[str, pd.DataFrame]) -> dict:
    """"Inline with previous studies, risky choice declined with age on average
    across conditions (b_age=-0.52, CI=[-1.01, -0.05], BF10=8.62)" — Ciranka &
    van den Bos, 2025, p.7, Results/Behavioural analyses."""
    df = _choice_df(data)
    model = smf.logit("response ~ age", data=df).fit(disp=0)
    effect_size = float(model.params["age"])
    reproduced = bool(model.params["age"] < 0 and model.pvalues["age"] < 0.05)
    return {
        "effect_name": "risky_choice_age_decline",
        "experiment": "exp0",
        "original_effect_size": -0.52,
        "effect_size": effect_size,
        "reproduced": reproduced,
    }


EFFECTS = [check_expected_value_risky_choice, check_social_risky_influence, check_risky_choice_age_decline]


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
