# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Wise, Michely, Dayan & Dolan (2019),
"A computational account of threat-related attentional bias", PLoS Comput Biol 15(10)
against any dataset in the Psych-301 unified schema (see schema.md).

The paper's headline findings concern visual attention (eye-tracking): value but not
uncertainty guides attention, and attention in turn biases value estimates. Eye-tracking
is absent from the uploaded CSV, so those effects are not testable here. The two headline
behavioural effects involving the shock-probability ratings and shock outcomes are:

Effects tested:
- threat_overestimation_bias (exp0): subjects overestimate low shock probabilities and
  underestimate high ones, i.e. estimation error (response - true shock probability) is
  negatively related to true shock probability. Per-subject OLS slope, one-sample t-test,
  expected negative and p<.05.
- asymmetric_learning_from_shock (exp0): subjects update probability ratings more after a
  shock outcome (upwards) than after a no-shock outcome (downwards), i.e. rating changes
  are larger following shock relative to no-shock, and on average positive after shock and
  negative after no-shock. Paired t-test, expected |up-shock| > |down-no-shock|, p<.05.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

EXPERIMENTS = ["exp0"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides, loads
    ./{exp}.csv from CWD — cd into a checkout of the dataset repo (or pass --<exp> path
    on the CLI) before running.

    Required columns for exp0: participant_id, task_id, trial, block, stimulus, response,
    shock_prob, shock, phase.
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def check_threat_overestimation_bias(data: dict[str, pd.DataFrame]) -> dict:
    """\"...shock probability was overestimated when true shock probability was low, and
    underestimated when it was high (S5 Fig)\" — Wise et al. 2019, p.11-12, Results
    (Aversive value estimates are influenced by visual attention)."""
    df = data["exp0"]
    df = df[(df["phase"] == "test")].dropna(subset=["response", "shock_prob"])
    betas = {}
    for pid, g in df.groupby("participant_id"):
        X = sm.add_constant(g["shock_prob"].values)
        est_error = (g["response"] - g["shock_prob"]).values
        if len(g) < 5 or np.all(g["shock_prob"] == g["shock_prob"].iloc[0]):
            continue
        m = sm.OLS(est_error, X).fit()
        betas[pid] = m.params[1]
    betas = np.array(list(betas.values()))
    t, p = stats.ttest_1samp(betas, 0)
    reproduced = bool(t < 0 and p < 0.05)
    return {
        "effect_name": "threat_overestimation_bias",
        "experiment": "exp0",
        "original_effect_size": -0.18,
        "effect_size": float(betas.mean()),
        "reproduced": reproduced,
        "t": float(t),
        "p": float(p),
    }


def check_asymmetric_learning_from_shock(data: dict[str, pd.DataFrame]) -> dict:
    """\"...subjects updated their estimates significantly more in response to shock
    compared to no-shock outcomes (t(47)=7.09, p<0.001), indicating a bias in learning
    such that subjects learned faster about negative compared to positive outcomes\" —
    Wise et al. 2019, p.8, Results (Threat likelihood estimation...)."""
    df = data["exp0"]
    df = df[(df["phase"] == "test") & df["shock"].notna()].copy()
    df = df.sort_values(["participant_id", "task_id", "stimulus", "trial"])
    df["prev_resp"] = df.groupby(["participant_id", "task_id", "stimulus"])["response"].shift(1)
    df["dresp"] = df["response"] - df["prev_resp"]
    d = df.dropna(subset=["dresp", "prev_resp"])
    pairs = []
    for pid, g in d.groupby("participant_id"):
        sh = g[g["shock"] == 1]["dresp"]
        ns = g[g["shock"] == 0]["dresp"]
        if len(sh) < 3 or len(ns) < 3:
            continue
        pairs.append((sh.mean(), ns.mean()))
    pairs = np.array(pairs)
    s = pairs[:, 0]
    ns = pairs[:, 1]
    t, p = stats.ttest_rel(s, ns)
    reproduced = bool(s.mean() > 0 and ns.mean() < 0 and t > 0 and p < 0.05)
    return {
        "effect_name": "asymmetric_learning_from_shock",
        "experiment": "exp0",
        "original_effect_size": 7.09,
        "effect_size": float(t),
        "reproduced": reproduced,
        "up_shock": float(s.mean()),
        "up_no_shock": float(ns.mean()),
        "p": float(p),
    }


EFFECTS = [check_threat_overestimation_bias, check_asymmetric_learning_from_shock]


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