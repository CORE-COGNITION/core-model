# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Olschewski, Spektor, & Le Mens (2024,
"Frequent winners explain apparent skewness preferences in experience-based decisions",
PNAS) against any dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- frequent_winner_study1 (exp0): in the sampling "broker game" trials of Study 1, participants
  choose the option that wins the majority of the 30 direct outcome comparisons ("frequent
  winner") above chance; one-sample t-test on per-participant proportions vs 0.5, expected > 0.5.
- frequent_winner_study2 (exp1): in Study 2 (which experimentally manipulates which of two
  skew-match option is the frequent winner, discrete and continuous), participants again choose
  the frequent winner above chance; one-sample t-test on per-participant proportions vs 0.5.
- intrinsic_right_skew_study3 (exp2): in Study 3's continuous condition (where neither option is
  a frequent winner), participants choose the right-skewed option above chance, revealing an
  intrinsic right-skew preference; one-sample t-test on per-participant proportions vs 0.5.
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0", "exp1", "exp2"]

# All sampling conditions whose direct outcome comparison defines a frequent winner.
STUDY1_CONDITIONS = ["normal", "disskewed", "conskewed"]
STUDY2_CONDITIONS = ["disleftwin", "disrightwin", "consleftwin", "consrightwin"]


def _fw_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add a boolean 'chose_fw' column: whether the participant chose the option that won the
    majority of the 30 paired direct outcome comparisons (frequent winner). NaN on ties."""
    left = [np.array(json.loads(v), dtype=float) for v in df["samples_left"]]
    right = [np.array(json.loads(v), dtype=float) for v in df["samples_right"]]
    lw = np.array([(l > r).sum() for l, r in zip(left, right)])
    rw = np.array([(r > l).sum() for l, r in zip(left, right)])
    fw_right = rw > lw
    fw_left = lw > rw
    df = df.copy()
    df["chose_fw"] = np.where(fw_right, df["response"] == 1,
                              np.where(fw_left, df["response"] == 0, np.nan))
    return df


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD — `cd` into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      exp0, exp1, exp2: participant_id, trial, response, condition, samples_left,
        samples_right, side_right
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _t_above_chance(x: np.ndarray) -> tuple[float, float]:
    t, p = stats.ttest_1samp(x, 0.5)
    return float(t), float(p)


def check_frequent_winner_study1(data: dict[str, pd.DataFrame]) -> dict:
    """"Across seven studies, we show that apparent preferences for left-skewed outcome
    distributions are a consequence of those distributions having a higher value in most direct
    outcome comparisons, a 'frequent-winner effect'." — Olschewski et al. 2024, Abstract.
    Study 1 (exp0), the confounded-skewness and Gaussian conditions."""
    df = _fw_columns(data["exp0"])
    sub = df[df["condition"].isin(STUDY1_CONDITIONS)]
    pp = sub.groupby("participant_id")["chose_fw"].mean().dropna().to_numpy()
    t, p = _t_above_chance(pp)
    reproduced = bool(pp.mean() > 0.5 and p < 0.05)
    # Study 1 report: Gaussian condition M=67.2%, t(98)=5.429; discrete M=60.1%; continuous M=57.6%.
    return {
        "effect_name": "frequent_winner_study1",
        "experiment": "exp0",
        "original_effect_size": 0.672,
        "effect_size": float(pp.mean()),
        "p": p,
        "t": t,
        "reproduced": reproduced,
    }


def check_frequent_winner_study2(data: dict[str, pd.DataFrame]) -> dict:
    """"By manipulating which option is the frequent winner, we show that choice tendencies for
    frequent winners can be obtained even with identical outcome distributions." — Olschewski et
    al. 2024, Abstract. Study 2 (exp1): discrete & continuous frequent-winner manipulation."""
    df = _fw_columns(data["exp1"])
    sub = df[df["condition"].isin(STUDY2_CONDITIONS)]
    pp = sub.groupby("participant_id")["chose_fw"].mean().dropna().to_numpy()
    t, p = _t_above_chance(pp)
    reproduced = bool(pp.mean() > 0.5 and p < 0.05)
    # Study 2 report: left-winner discrete M=67.1%, right-winner discrete left=21.4%,
    # left-winner continuous M=60.1%, right-winner continuous left=31.0%.
    return {
        "effect_name": "frequent_winner_study2",
        "experiment": "exp1",
        "original_effect_size": 0.671,
        "effect_size": float(pp.mean()),
        "p": p,
        "t": t,
        "reproduced": reproduced,
    }


def check_intrinsic_right_skew_study3(data: dict[str, pd.DataFrame]) -> dict:
    """"The results of this study provide partial support for the hypothesis that participants
    have an intrinsic preference for right-skewed outcome distributions." — Olschewski et al. 2024,
    p.4, Study 3. Continuous condition (exp2) where neither option is the frequent winner."""
    df = data["exp2"]
    sub = df[df["condition"] == "consequal"]
    # right-skewed option is chosen when response == side_right (side_right=1 iff right is
    # right-skewed); left-skewed when response == 1 - side_right.
    sub = sub.copy()
    sub["chose_rskew"] = (sub["response"] == sub["side_right"]).astype(float)
    pp = sub.groupby("participant_id")["chose_rskew"].mean().to_numpy()
    t, p = _t_above_chance(pp)
    reproduced = bool(pp.mean() > 0.5 and p < 0.05)
    # Study 3 continuous report: left-skewed M=45.8% (i.e. right-skewed 54.2%), t(249)=-3.423, p=.001.
    return {
        "effect_name": "intrinsic_right_skew_study3",
        "experiment": "exp2",
        "original_effect_size": 0.542,
        "effect_size": float(pp.mean()),
        "p": p,
        "t": t,
        "reproduced": reproduced,
    }


EFFECTS = [check_frequent_winner_study1, check_frequent_winner_study2,
           check_intrinsic_right_skew_study3]


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
