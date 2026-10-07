# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Günther et al. (2023) "ViSpa" (Vision Spaces)
against any dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- discrimination_similarity_rt (exp3): For pairs of different but very similar images,
  participants are SLOWER than for less similar pairs. Test: Pearson correlation between
  image similarity (IMG, layer 6) and log mean RT across item-level data; expected positive.
- discrimination_similarity_errors (exp3): For pairs of different but very similar images,
  participants make MORE errors than for less similar pairs. Test: Pearson correlation
  between image similarity (IMG, layer 6) and error rate (1 - percent correct); expected positive.
- priming_accuracy_above_chance (exp4): Overall accuracy in the visual-decision (priming)
  task is high, far above the 50% chance level. Test: one-sample proportion test that mean
  per-trial accuracy > 0.5.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats as st

EXPERIMENTS = ["exp3", "exp4"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides, loads
    ./{exp}.csv from CWD.

    Required columns per experiment:
      exp3: pair, Image1, Image2, rt, logRT, response, Value, IMG_Simil_L6
      exp4: participant_id, trial, response, rt, phase
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _sim_col(df: pd.DataFrame, pref: str) -> str:
    cands = [
        "IMG_Simil_L6",
        "IMG_Simil",
        "Value",
        pref,
    ]
    for c in cands:
        if c in df.columns:
            return c
    return df.columns[0]


def check_discrimination_similarity_rt(data: dict[str, pd.DataFrame]) -> dict:
    """\"...correct 'different' responses are typically fewer and slower the more similar the
    stimuli are...\" — Günther et al. 2023, p.52, Study 4 (Method)."""
    df = data["exp3"]
    sim = _sim_col(df, "IMG_Simil_L6")
    rt = df["logRT"] if "logRT" in df.columns else np.log(df["rt"])
    r, p = st.pearsonr(df[sim], rt)
    reproduced = bool(r > 0 and p < 0.05)
    return {
        "effect_name": "discrimination_similarity_rt",
        "experiment": "exp3",
        "original_effect_size": 0.110,  # R2adj of IMG smooth on RT in the paper
        "effect_size": float(r),
        "p": float(p),
        "reproduced": reproduced,
    }


def check_discrimination_similarity_errors(data: dict[str, pd.DataFrame]) -> dict:
    """\"...made more errors in their judgments, than when evaluating two less similar
    images...\" — Günther et al. 2023, p.59, Study 4 (Discussion)."""
    df = data["exp3"]
    sim = _sim_col(df, "IMG_Simil_L6")
    err = 1.0 - df["response"]
    r, p = st.pearsonr(df[sim], err)
    reproduced = bool(r > 0 and p < 0.05)
    return {
        "effect_name": "discrimination_similarity_errors",
        "experiment": "exp3",
        "original_effect_size": None,  # paper reports smooth-term F=129.7, p<.001 on error rate
        "effect_size": float(r),
        "p": float(p),
        "reproduced": reproduced,
    }


def check_priming_accuracy_above_chance(data: dict[str, pd.DataFrame]) -> dict:
    """\"...participants were presented with target images and had to indicate whether the
    target was a real image...\" (priming/visual-decision accuracy well above chance)."""
    df = data["exp4"]
    if "phase" in df.columns:
        df = df[df["phase"] == "experiment"]
    acc = df["response"].astype(float).dropna()
    n = len(acc)
    k = int(acc.sum())
    z = ratio = acc.mean()
    p = st.wilcoxon if False else None
    # one-sample proportion test H0: p=0.5, H1: p>0.5
    pval = st.binomtest(k, n, 0.5, alternative="greater").pvalue
    reproduced = bool(ratio > 0.5 and pval < 0.05)
    return {
        "effect_name": "priming_accuracy_above_chance",
        "experiment": "exp4",
        "original_effect_size": 0.5,  # chance level
        "effect_size": float(ratio),
        "p": float(pval),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_discrimination_similarity_rt,
    check_discrimination_similarity_errors,
    check_priming_accuracy_above_chance,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. No printing."""
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
    print(f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  {'p':>10}  reproduced")
    for r in results:
        o = r["original_effect_size"]
        os = "    n/a" if o is None else f"{o:10.3f}"
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  {os}  "
              f"{r['effect_size']:>10.3f}  {r['p']:>10.3g}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()