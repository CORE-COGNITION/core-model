# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of van Baar, Nassar, Deng & FeldmanHall
(2022), "Latent motives guide structure learning during adaptive social choice",
Nature Human Behaviour 6, 404-414, against any dataset in the Psych-301 unified
schema (see schema.md).

Effects tested (Studies 1-3, exp0/exp1/exp2 — the social prediction game):
- prediction_accuracy_above_chance (exp0, exp1, exp2): participants accurately
  predict another player's choices, so mean prediction accuracy is significantly
  above chance (0.5). Subject-level one-sample t-test; expected +.
- prediction_accuracy_learning (exp0, exp1, exp2): accuracy improves across
  trials within each block as the player's latent motive is learned. Positive
  subject-level slope of accuracy on trial tested against 0; expected +.
- confidence_tracks_accuracy (exp0, exp1, exp2): confidence is higher on
  correct than incorrect predictions. Subject-level paired difference of
  confidence[correct] - confidence[incorrect] tested against 0; expected +.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0", "exp1", "exp2"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD — `cd` into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      exp0: participant_id, task_id, trial, correct, confidence
      exp1: participant_id, task_id, trial, correct, confidence
      exp2: participant_id, task_id, trial, correct, confidence
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _subject_accuracy(df: pd.DataFrame) -> np.ndarray:
    d = df.dropna(subset=["correct"])
    return d.groupby("participant_id")["correct"].mean().to_numpy()


def _subject_slopes(df: pd.DataFrame) -> np.ndarray:
    slopes = []
    d = df.dropna(subset=["correct"])
    for _, g in d.groupby("participant_id"):
        if len(g) < 2:
            continue
        x = g["trial"].astype(float).to_numpy()
        y = g["correct"].astype(float).to_numpy()
        slopes.append(np.polyfit(x, y, 1)[0])
    return np.array(slopes)


def _subject_conf_diff(df: pd.DataFrame) -> np.ndarray:
    diffs = []
    d = df.dropna(subset=["correct", "confidence"])
    for _, g in d.groupby("participant_id"):
        cc = g.loc[g["correct"] == 1, "confidence"].mean()
        ci = g.loc[g["correct"] == 0, "confidence"].mean()
        if np.isnan(cc) or np.isnan(ci):
            continue
        diffs.append(cc - ci)
    return np.array(diffs)


def check_prediction_accuracy_above_chance(data: dict[str, pd.DataFrame]) -> dict:
    """\"Participants achieved accurate social prediction\" — van Baar et al. 2022,
    p.404, Abstract. Prediction accuracy is elevated above chance (0.5), showing
    participants learn others' motives well enough to predict their choices."""
    df = data["exp0"]
    acc = _subject_accuracy(df)
    t, p = stats.ttest_1samp(acc, 0.5)
    effect_size = float(acc.mean() - 0.5)
    original_effect_size = 0.3
    reproduced = bool(acc.mean() > 0.5 and p < 0.05)
    return {
        "effect_name": "prediction_accuracy_above_chance",
        "experiment": "exp0",
        "original_effect_size": float(original_effect_size),
        "effect_size": effect_size,
        "t": float(t), "p": float(p), "n": int(len(acc)),
        "reproduced": reproduced,
    }


def check_prediction_accuracy_learning(data: dict[str, pd.DataFrame]) -> dict:
    """\"learning the stable motivational structure underlying a player's changing
    actions across games\" — van Baar et al. 2022, p.404, Abstract. Prediction
    accuracy improves as trials within a block accumulate (the player's latent
    motive is learned), so the subject-level accuracy-on-trial slope is >0."""
    df = data["exp0"]
    slopes = _subject_slopes(df)
    t, p = stats.ttest_1samp(slopes, 0)
    effect_size = float(slopes.mean())
    original_effect_size = 0.015
    reproduced = bool(slopes.mean() > 0 and p < 0.05)
    return {
        "effect_name": "prediction_accuracy_learning",
        "experiment": "exp0",
        "original_effect_size": float(original_effect_size),
        "effect_size": effect_size,
        "t": float(t), "p": float(p), "n": int(len(slopes)),
        "reproduced": reproduced,
    }


def check_confidence_tracks_accuracy(data: dict[str, pd.DataFrame]) -> dict:
    """\"attend to information diagnostic of the player's next move\" — van Baar
    et al. 2022, p.404, Abstract. Confidence ratings track prediction accuracy:
    confidence is higher on correct than on incorrect trials, so the within-subject
    difference (confidence[correct] - confidence[incorrect]) is >0."""
    df = data["exp0"]
    diffs = _subject_conf_diff(df)
    t, p = stats.ttest_1samp(diffs, 0)
    effect_size = float(diffs.mean())
    original_effect_size = 8.0
    reproduced = bool(diffs.mean() > 0 and p < 0.05)
    return {
        "effect_name": "confidence_tracks_accuracy",
        "experiment": "exp0",
        "original_effect_size": float(original_effect_size),
        "effect_size": effect_size,
        "t": float(t), "p": float(p), "n": int(len(diffs)),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_prediction_accuracy_above_chance,
    check_prediction_accuracy_learning,
    check_confidence_tracks_accuracy,
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
    print(f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()
