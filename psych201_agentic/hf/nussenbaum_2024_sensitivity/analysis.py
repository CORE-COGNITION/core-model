# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Nussenbaum et al. (2024), "Sensitivity to the
Instrumental Value of Choice Increases Across Development" (Psychol Sci 35(8):933-947)
against any dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- sensitivity_instrumental_value (exp0): participants choose agency more often as the
  instrumental value of choice (VoC = EV_choose - EV_forgo) increases. Positive main effect
  of VoC on agency choice (the paper: beta = 1.42, p < .001).
- sensitivity_instrumental_value (exp1): replicated in the online preregistered study
  (the paper: beta = 1.42 Exp1; VoC main effect p < .001 in both experiments).
- developmental_increase_in_sensitivity (exp1): the Age x VoC interaction is positive and
  significant -- older participants show greater sensitivity to the value of choice
  (the paper: beta = 0.22, p < .001 in Exp2; the decisive preregistered replication).
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

EXPERIMENTS = ["exp0", "exp1"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides, loads
    ./{exp}.csv from CWD -- `cd` into a checkout of the dataset repo (or pass --<exp>
    path on the CLI) before running.

    Required columns per experiment:
      exp0: participant_id, stage, agency, voc, age, valid
      exp1: participant_id, stage, stage_1_choice, reward_prob_L/R, offer, age, valid
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _agency_rows(df: pd.DataFrame, exp: str) -> pd.DataFrame:
    """Return valid agency-stage trials with a computed value-of-choice (voc) column."""
    d = df[(df["stage"] == "agency")].copy()
    if exp == "exp1":
        d["voc"] = (
            d[["reward_prob_L", "reward_prob_R"]].max(axis=1) * 10
            - (d[["reward_prob_L", "reward_prob_R"]].mean(axis=1) * 10 + d["offer"])
        )
        d["agency"] = d["stage_1_choice"]
    else:
        d["voc"] = d["voc"]
        d["agency"] = d["agency"]
    d = d[d["valid"] == 1]
    return d


def _vocation_regression(d: pd.DataFrame):
    """OLS of agency on centered VoC, age and their interaction, cluster-robust by subject."""
    d = d.copy()
    d["vo_c"] = d["voc"] - d["voc"].mean()
    d["ag_c"] = d["age"] - d["age"].mean()
    d["inter"] = d["vo_c"] * d["ag_c"]
    X = sm.add_constant(d[["vo_c", "ag_c", "inter"]])
    y = d["agency"].values.astype(float)
    m = sm.OLS(y, X)
    r = m.fit(cov_type="cluster", cov_kwds={"groups": d["participant_id"]})
    return r


def _p_from_r(r, name):
    b = r.params[name]
    se = r.bse[name]
    z = b / se
    return float(2 * (1 - stats.norm.cdf(abs(z))))


def check_sensitivity_instrumental_value_exp0(data):
    """\"Participants demonstrated sensitivity to the value of choice: They were more likely
    to choose agency when doing so had higher expected value, beta = 1.42, SE = 0.07,
    chi2(1) = 144.39, p < .001\" -- Nussenbaum et al., p.936, Exp 1 Results."""
    d = _agency_rows(data["exp0"], "exp0")
    r = _vocation_regression(d)
    effect = float(r.params["vo_c"])
    p = _p_from_r(r, "vo_c")
    reproduced = effect > 0 and p < 0.05
    return {
        "effect_name": "sensitivity_instrumental_value_exp0",
        "experiment": "exp0",
        "original_effect_size": 1.42,
        "effect_size": effect,
        "reproduced": bool(reproduced),
    }


def check_sensitivity_instrumental_value_exp1(data):
    """\"We replicated our original finding... participants were more likely to choose agency
    when doing so had higher expected value\" -- Nussenbaum et al., Exp 2 Results (VoC main
    effect p < .001)."""
    d = _agency_rows(data["exp1"], "exp1")
    r = _vocation_regression(d)
    effect = float(r.params["vo_c"])
    p = _p_from_r(r, "vo_c")
    reproduced = effect > 0 and p < 0.05
    return {
        "effect_name": "sensitivity_instrumental_value_exp1",
        "experiment": "exp1",
        "original_effect_size": 1.42,
        "effect_size": effect,
        "reproduced": bool(reproduced),
    }


def check_developmental_increase_exp1(data):
    """\"We replicated our original finding of an Age x VoC interaction effect on agentic
    choice, beta = 0.22, SE = .06, chi2(1) = 12.28, p < .001: Older participants demonstrated
    greater sensitivity to the value of choice\" -- Nussenbaum et al., p.941, Exp 2 Results."""
    d = _agency_rows(data["exp1"], "exp1")
    r = _vocation_regression(d)
    effect = float(r.params["inter"])
    p = _p_from_r(r, "inter")
    reproduced = effect > 0 and p < 0.05
    return {
        "effect_name": "developmental_increase_in_sensitivity",
        "experiment": "exp1",
        "original_effect_size": 0.22,
        "effect_size": effect,
        "reproduced": bool(reproduced),
    }


EFFECTS = [
    check_sensitivity_instrumental_value_exp0,
    check_sensitivity_instrumental_value_exp1,
    check_developmental_increase_exp1,
]


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


if __name__ == "__main__":
    main()
