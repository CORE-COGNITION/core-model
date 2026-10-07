# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Gershman (2018), "Deconstructing the
human algorithms for exploration", Cognition 173, 34-42, against any dataset
in the Psych-301 unified schema (see schema.md).

Effects tested:
- value_directed_choice (exp0, exp1): per-subject probit coefficient on the
  Kalman-filter value difference V (value-only model, no intercept) is positive
  on average (one-sample t-test, t > 0, p < .05 in both experiments; recovers
  the value-sensitivity of choice underlying the paper's model comparison,
  Results 4.1).
- directed_exploration_ru (exp0, exp1): in the V + RU + V/TU probit, the
  relative-uncertainty coefficient RU is positive on average (paper: Exp 1
  t(44)=5.41, p < .001; Exp 2 t(43)=5.16, p < .001), i.e. directed (UCB-style)
  exploration.
- random_exploration_vtu (exp0, exp1): in the same probit, the V/TU coefficient
  is positive on average (paper: Exp 1 t(44)=3.28, p < .005; Exp 2 t(43)=5.02,
  p < .001), i.e. random (Thompson-style) exploration scaling with total
  uncertainty.
- first_trial_uncertainty_preference (exp0, exp1): on the first trial of each
  block participants prefer the risky arm 1 in Exp 1 (P(arm 1) > .5; paper:
  t(44)=9.68, p < .001) and show NO such preference in Exp 2, where both arms
  have equal prior uncertainty (paper: p = .95; reproduces as p > .05).
"""
from __future__ import annotations

import argparse
import warnings

import numpy as np
import pandas as pd
from scipy.stats import ttest_1samp
import statsmodels.api as sm

warnings.filterwarnings("ignore")

EXPERIMENTS = ["exp0", "exp1"]

# (prior variance, reward variance) of arms 1 and 2 per experiment, as in the
# paper's Appendix ("Experiment 1, tau0^2(1)=10, tau0^2(2)=0, tau^2(1)=10,
# tau^2(2)=0; Experiment 2, tau0^2 = 100/100, tau^2 = 10/10").
DESIGNS = {
    "exp0": {"tau0": (10.0, 0.0), "tau2": (10.0, 0.0)},
    "exp1": {"tau0": (100.0, 100.0), "tau2": (10.0, 10.0)},
}


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD — `cd` into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      exp0: participant_id, task_id, trial, response, reward, rt
      exp1: participant_id, task_id, trial, response, reward, rt
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _kalman_regressors(g: pd.DataFrame, tau0: tuple, tau2: tuple):
    """Kalman-filter latents as in the paper's Appendix, reset at each task_id
    (each block is a fresh bandit with newly drawn arm means).

    Returns arrays V = Q1-Q2, RU = sqrt(s1)-sqrt(s2), TU = sqrt(s1+s2)
    evaluated *before* each trial's reward is observed.
    """
    q1, q2 = 0.0, 0.0
    s1, s2 = tau0
    prev = -1
    vs, rus, tus = [], [], []
    for _, r in g.iterrows():
        if r.task_id != prev:
            q1, q2 = 0.0, 0.0
            s1, s2 = tau0
            prev = r.task_id
        vs.append(q1 - q2)
        rus.append(np.sqrt(max(s1, 0.0)) - np.sqrt(max(s2, 0.0)))
        tus.append(np.sqrt(s1 + s2))
        if r.response == 0:
            d0 = s1 + tau2[0]
            a = s1 / d0 if d0 > 0 else 0.0
            q1 += a * (r.reward - q1)
            s1 -= a * s1
        else:
            d0 = s2 + tau2[1]
            a = s2 / d0 if d0 > 0 else 0.0
            q2 += a * (r.reward - q2)
            s2 -= a * s2
    return np.array(vs), np.array(rus), np.array(tus)


def _subject_coefficients(df: pd.DataFrame, cols: list[str],
                          tau0: tuple, tau2: tuple, rt_cut: float = 20000.0
                          ) -> pd.DataFrame:
    """Per-subject probit coefficients (no intercept, as the paper's glmfit
    'constant off'), pooling all trials of a subject (paper excludes
    RT > 20 s, as in load_data.m)."""
    if rt_cut is not None:
        df = df[df.rt < rt_cut]
    coefs = []
    for pid, g in df.groupby("participant_id"):
        g = g.sort_values(["task_id", "trial"])
        v, ru, tu = _kalman_regressors(g, tau0, tau2)
        y = (g.response == 0).astype(float).values  # 1 = arm 1 chosen
        x = {"V": v, "RU": ru, "VTU": v / np.maximum(tu, 1e-9)}
        X = np.column_stack([x[c] for c in cols])
        try:
            fit = sm.Probit(y, X).fit(disp=False, maxiter=500)
        except Exception:
            continue
        coefs.append(fit.params)
    return pd.DataFrame(coefs, columns=cols)


def _t_stats(coefs: pd.DataFrame) -> dict:
    """{col: (t, p, mean) from a one-sample t-test of the per-subject
    coefficients against 0, matching the paper's `[~,p] = ttest(b)`."""
    return {c: ttest_1samp(coefs[c], 0.0) for c in coefs.columns}


def check_value_directed_choice(data: dict[str, pd.DataFrame]) -> dict:
    """\"we included a 'value-directed exploration' model in which the choice
    probability was only a function of the value difference (i.e., no
    dependence on uncertainty)\" — Gershman, 2018, p. 37, Results 4.1.
    (The paper reports V alone only as null inside the hybrid model; the
    value-only model check below recovers the value-sensitivity of choice.)"""
    ok, ds = True, []
    for exp in EXPERIMENTS:
        df = data[exp]
        d = DESIGNS[exp]
        c = _subject_coefficients(df, ["V"], d["tau0"], d["tau2"])
        t, p = _t_stats(c)["V"]
        ok = ok and t > 0 and p < 0.05
        ds.append(t / np.sqrt(len(c)))
    return {
        "effect_name": "value_directed_choice",
        "experiment": "exp0,exp1",
        "original_effect_size": 0.0,
        "effect_size": float(np.mean(ds)),
        "reproduced": bool(ok),
        "t": float(np.round(t, 2)),
        "p": float(p),
    }


def check_directed_exploration_ru(data: dict[str, pd.DataFrame]) -> dict:
    """\"The probit regression analysis of the Experiment 1 data (Figure 2,
    bottom) revealed effects of both RU [t(44) = 5.41, p < 0.001] ...
    largely consistent with the results of Experiment 1, revealing effects of
    both RU [t(43) = 5.16, p < 0.001]\" — Gershman, 2018, p. 37, Results 4.1."""
    ok, ds = True, []
    for exp in EXPERIMENTS:
        df = data[exp]
        d = DESIGNS[exp]
        c = _subject_coefficients(df, ["V", "RU", "VTU"], d["tau0"], d["tau2"])
        t, p = _t_stats(c)["RU"]
        ok = ok and t > 0 and p < 0.05
        ds.append(t / np.sqrt(len(c)))
    return {
        "effect_name": "directed_exploration_ru",
        "experiment": "exp0,exp1",
        "original_effect_size": float(np.mean([5.41 / np.sqrt(45), 5.16 / np.sqrt(44)])),
        "effect_size": float(np.mean(ds)),
        "reproduced": bool(ok),
        "t": float(np.round(t, 2)),
        "p": float(p),
    }


def check_random_exploration_vtu(data: dict[str, pd.DataFrame]) -> dict:
    """\"...revealing effects of both RU [t(44) = 5.41, p < 0.001] and V/TU
    [t(44) = 3.28, p < 0.005]... revealing effects of both RU [t(43) = 5.16,
    p < 0.001] and TU [t(43) = 5.02, p < 0.001]\" — Gershman, 2018, p. 37,
    Results 4.1."""
    ok, ds = True, []
    for exp in EXPERIMENTS:
        df = data[exp]
        d = DESIGNS[exp]
        c = _subject_coefficients(df, ["V", "RU", "VTU"], d["tau0"], d["tau2"])
        t, p = _t_stats(c)["VTU"]
        ok = ok and t > 0 and p < 0.05
        ds.append(t / np.sqrt(len(c)))
    return {
        "effect_name": "random_exploration_vtu",
        "experiment": "exp0,exp1",
        "original_effect_size": float(np.mean([3.28 / np.sqrt(45), 5.02 / np.sqrt(44)])),
        "effect_size": float(np.mean(ds)),
        "reproduced": bool(ok),
        "t": float(np.round(t, 2)),
        "p": float(p),
    }


def check_first_trial_uncertainty_preference(data: dict[str, pd.DataFrame]) -> dict:
    """\"Consistent with this hypothesis, we found that participants preferred
    arm 1 on the first trial [t(44) = 9.68, p < 0.001; Figure 5]. In
    Experiment 2, no such differential uncertainty exists... Accordingly, we
    found no preference for arm 1 in Experiment 2 (p = 0.95; Figure 5)\" —
    Gershman, 2018, p. 38, Results 4.2."""
    ok = True
    ds = []
    for exp in EXPERIMENTS:
        df = data[exp]
        first = df[df.trial == 0]
        p1 = 1.0 - first.groupby("participant_id")["response"].mean()  # P(arm 1)
        t, p = ttest_1samp(p1, 0.5)
        ds.append(t / np.sqrt(len(p1)))
        if exp == "exp0":
            ok = ok and p1.mean() > 0.5 and p < 0.05
        else:  # the paper's claim for exp1 is the *absence* of a preference
            ok = ok and p > 0.05
    return {
        "effect_name": "first_trial_uncertainty_preference",
        "experiment": "exp0,exp1",
        "original_effect_size": float(9.68 / np.sqrt(45)),
        "effect_size": float(np.mean(ds)),
        "reproduced": bool(ok),
        "t": float(np.round(t, 2)),
        "p": float(p),
    }


EFFECTS = [
    check_value_directed_choice,
    check_directed_exploration_ru,
    check_random_exploration_vtu,
    check_first_trial_uncertainty_preference,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. No printing — pure return
    value so downstream simulators / model evaluators can call this
    programmatically."""
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
    print(f"{'effect':<{w}}  {'exp':<8}  {'orig':>10}  {'this':>10}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<8}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()