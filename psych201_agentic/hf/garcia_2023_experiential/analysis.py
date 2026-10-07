# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Garcia, Lebreton, Bourgeois-Gironde &
Palminteri (2023), "The impassable gap between experiential and symbolic values",
Nature Human Behaviour, against any dataset in the Psych-301 unified schema
(see schema.md).

Effects tested:
- experiential_learning_accuracy (LE, all exps): mean free-choice accuracy in the
  experiential-learning (LE) phase is above chance (0.5); paired/conceptual t-test
  of per-participant accuracy against 0.5, expected accuracy > 0.5 (positive).
- learning_sensitive_to_decision_value (LE, all exps): LE accuracy increases with the
  decision value (absolute EV difference of the pair, |ev1-ev2|); linear correlation
  positive and significant.
- experiential_value_neglect_es (ES, all exps): in hybrid ES choices, the probability
  of choosing the experiential (E-) option decreases as the symbolic (S-) lottery EV
  increases -- choices tracked the symbolic value, so the slope of P(choose E) on
  ev2 is negative and significant.
"""
from __future__ import annotations

import argparse
from typing import Callable

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

EXPERIMENTS = ["exp0", "exp1", "exp2", "exp3", "exp4", "exp5", "exp6", "exp7", "exp8"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD.

    Required columns: participant_id, phase, trial, response, reward, ev1, ev2
    (and: correct, condition, catch_trial).
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _test_rows(df: pd.DataFrame, phase: str) -> pd.DataFrame:
    """Keep freely-chosen test trials of a given phase (exclude practice/train,
    driver/catch trials). sess >= 0 marks real test sessions (-1/-2 = training)."""
    d = df[df["phase"] == phase].copy()
    if "sess" in d.columns:
        d = d[d["sess"] >= 0]
    if "catch_trial" in d.columns:
        d = d[d["catch_trial"] != 1]
    return d


def check_experiential_learning_accuracy(data: dict[str, pd.DataFrame]) -> dict:
    """"Apart from the most difficult learning context (60/40), choice accuracy was
    above chance level for all E-option pairs ... thus indicating that subjects aimed
    at (and managed to) maximize expected value." -- Garcia et al. 2023, p.4, Results
    (First evidence), exp0..exp8, LE phase."""
    pool_acc = []
    for exp in EXPERIMENTS:
        le = _test_rows(data[exp], "LE")
        if "correct" in le.columns and le["correct"].notna().any():
            acc = le.dropna(subset=["correct"]).groupby("participant_id")["correct"].mean()
            pool_acc.append(acc.mean())
    eff = float(np.mean(pool_acc))
    t, p = stats.ttest_1samp(np.asarray(pool_acc), 0.5)
    reproduced = bool(eff > 0.5 and t > 0 and p < 0.05)
    return {
        "effect_name": "experiential_learning_accuracy",
        "experiment": "exp0..exp8 LE",
        "original_effect_size": 0.66,
        "effect_size": eff,
        "reproduced": reproduced,
    }


def check_learning_sensitive_to_decision_value(data: dict[str, pd.DataFrame]) -> dict:
    """"Choice accuracy increased as a function of the decision value (β=0.077 ...
    P<0.05), thus indicating that subjects' behavior was sensitive to the specific EV
    of E-options involved in a given pair." -- Garcia et al. 2023, p.4, Results
    (First evidence), exp0..exp8, LE phase."""
    rs, ps = [], []
    for exp in EXPERIMENTS:
        le = _test_rows(data[exp], "LE")
        if le.empty or "correct" not in le.columns:
            continue
        le = le.dropna(subset=["correct", "ev1", "ev2"])
        dv = (le["ev1"] - le["ev2"]).abs()
        if le["correct"].nunique() < 2 or dv.nunique() < 2:
            continue
        r, p = stats.pearsonr(dv, le["correct"])
        rs.append(r)
        ps.append(p)
    eff = float(np.mean(rs))
    p_avg = float(np.mean(ps))
    reproduced = bool(eff > 0 and p_avg < 0.05)
    return {
        "effect_name": "learning_sensitive_to_decision_value",
        "experiment": "exp0..exp8 LE",
        "original_effect_size": 0.077,
        "effect_size": eff,
        "reproduced": reproduced,
    }


def check_experiential_value_neglect_es(data: dict[str, pd.DataFrame]) -> dict:
    """"Subjects pick the lottery, when positive, and reject it when negative, as if
    the E-option values were neglected and regressed to zero (experiential value
    neglect)." -- Garcia et al. 2023, p.4, Results (experiential value neglect),
    exp0..exp8, ES phase. Choices track symbolic value => P(choose E) decreases with
    the S-option EV (negative slope)."""
    betas, ps = [], []
    for exp in EXPERIMENTS:
        es = _test_rows(data[exp], "ES")
        if es.empty:
            continue
        # E-option is op1 (op1=="E"), response==1 => choose E.
        ce = (es["response"] == 1).astype(float)
        g = es.dropna(subset=["ev2"])
        if len(g) < 50:
            continue
        X = sm.add_constant(g["ev2"])
        try:
            fit = sm.OLS((es.loc[g.index, "response"] == 1).astype(float), X).fit()
        except Exception:
            continue
        betas.append(float(fit.params["ev2"]))
        ps.append(float(fit.pvalues["ev2"]))
    eff = float(np.mean(betas))
    p_avg = float(np.mean(ps))
    reproduced = bool(eff < 0 and p_avg < 0.05)
    return {
        "effect_name": "experiential_value_neglect_es",
        "experiment": "exp0..exp8 ES",
        "original_effect_size": -0.5,
        "effect_size": eff,
        "reproduced": reproduced,
    }


EFFECTS: list[Callable[[dict[str, pd.DataFrame]], dict]] = [
    check_experiential_learning_accuracy,
    check_learning_sensitive_to_decision_value,
    check_experiential_value_neglect_es,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order."""
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None, help=f"CSV path for {exp}; defaults to ./{exp}.csv")
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS if getattr(args, exp)}
    for exp in EXPERIMENTS:
        print(f"{exp}: {sources[exp] if exp in sources else '(default - local ./{exp}.csv)'}")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<14}  {'orig':>10}  {'this':>10}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<14}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()