# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Dentella, Günther & Leivada (2023,
PNAS, "Systematic testing of three Language Models reveals low language
accuracy, absence of response stability, and a yes response bias") against any
dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- overall_accuracy_above_chance (exp0): human mean accuracy across all test
  sentences is significantly above chance (0.5). One-sample t-test on per-
  participant accuracy; expected direction: mean > 0.5.
- accuracy_above_chance_ungrammatical (exp0): human accuracy is above chance
  even for ungrammatical sentences (unlike the tested LMs, which perform at
  chance there). One-sample t-test on per-participant ungrammatical accuracy;
  expected direction: mean > 0.5.
- human_response_stability (exp0): humans give stable responses — the rate of
  oscillations (a change from the previous judgment of the same sentence) is
  significantly below 0.5. One-sample t-test on per-participant oscillation
  rate (stability==1 encodes a change); expected direction: mean < 0.5.
"""
from __future__ import annotations

import argparse
import pandas as pd
import numpy as np
from scipy import stats

EXPERIMENTS = ["exp0"]

CHANCE = 0.5
TEST_QUERIES = {"condition": "no", "phenomenon": "no"}


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD.

    Required columns per experiment:
      exp0: participant_id, trial, response, condition, correct, repetition, stability
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _test_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Drop attention-check rows (paper excludes them from analyses)."""
    return df[df["phenomenon"] != "attention check"]


def check_overall_accuracy_above_chance(data: dict[str, pd.DataFrame]) -> dict:
    """\"Humans are universally good in providing stable and accurate judgments...
    and critically well above chance for both grammatical and ungrammatical
    sentences\" — Dentella et al. 2023, p.5 (Comparisons with Human Data,
    Accuracy; see also Abstract/Discussion)."""
    df = _test_rows(data["exp0"])
    acc = df.groupby("participant_id")["correct"].mean()
    t, p = stats.ttest_1samp(acc, CHANCE)
    reproduced = bool(acc.mean() > CHANCE and p < 0.05)
    return {
        "effect_name": "overall_accuracy_above_chance",
        "experiment": "exp0",
        "original_effect_size": CHANCE,
        "effect_size": float(acc.mean()),
        "p": float(p),
        "reproduced": reproduced,
    }


def check_accuracy_above_chance_ungrammatical(data: dict[str, pd.DataFrame]) -> dict:
    """\"...no LM performs above chance when questioned on ungrammatical prompts,
    as opposed to humans, whose accuracy is well above chance for both
    grammatical and ungrammatical sentences\" — Dentella et al. 2023, p.8
    (Discussion)."""
    df = _test_rows(data["exp0"])
    ung = df[df["condition"] == "ungrammatical"]
    acc = ung.groupby("participant_id")["correct"].mean()
    t, p = stats.ttest_1samp(acc, CHANCE)
    reproduced = bool(acc.mean() > CHANCE and p < 0.05)
    return {
        "effect_name": "accuracy_above_chance_ungrammatical",
        "experiment": "exp0",
        "original_effect_size": CHANCE,
        "effect_size": float(acc.mean()),
        "p": float(p),
        "reproduced": reproduced,
    }


def check_human_response_stability(data: dict[str, pd.DataFrame]) -> dict:
    """\"...humans show fewer oscillations the more often they respond to the
    same prompt\" and \"Humans exhibit a more stable response pattern than LMs\"
    — Dentella et al. 2023, p.5-6 (Comparisons with Human Data, Stability)."""
    df = _test_rows(data["exp0"])
    sub = df.sort_values(["participant_id", "sentence", "repetition"])
    osc = sub[sub["stability"].notna()].groupby("participant_id")["stability"].mean()
    t, p = stats.ttest_1samp(osc, CHANCE)
    reproduced = bool(osc.mean() < CHANCE and p < 0.05)
    return {
        "effect_name": "human_response_stability",
        "experiment": "exp0",
        "original_effect_size": CHANCE,
        "effect_size": float(osc.mean()),
        "p": float(p),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_overall_accuracy_above_chance,
    check_accuracy_above_chance_ungrammatical,
    check_human_response_stability,
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
    print(f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  p        reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{r['p']:.4f}  {'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()
