# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "scipy"]
# ///
"""Check the primary behavioral effects of Steingroever et al. (2015), "Data from 617
Healthy Participants Performing the Iowa Gambling Task: A Many Labs Collaboration"
(Journal of Open Psychology Data 3:e5), against any dataset in the Psych-301 unified
schema (see schema.md).

This is a data-paper; it reports no inferential statistics of its own, so the primary
behavioral claim is the classic Iowa Gambling Task (IGT) learning effect that the pooled
healthy data are expected to exhibit: participants learn to prefer the advantageous decks
(C/D) over the disadvantageous decks (A/B), so the net score (C+D minus A+B, per block /
participant) increases across trial blocks and is significantly positive in the later
blocks. Checked on the 100-trial group (exp1) which has the largest N (504 subjects).

Effects tested:
- igt_learning_net_score_increase (exp1): within-participant net advantage/choice score in
  the final block of 10 trials exceeds that in the first block (paired t-test, positive diff).
- igt_learning_advantageous_late_blocks (exp1): within-participant net score in the final
  block is significantly positive (one-sample t-test against 0), i.e. C/D chosen over A/B.
"""
from __future__ import annotations

import argparse

import pandas as pd
import numpy as np
from scipy import stats
import scipy

EXPERIMENTS = ["exp0", "exp1", "exp2"]

response_labels = {
    "exp0": "1=A,B=2,C=3,D=4 (1-indexed); response==deck_choice",
    "exp1": "1=A,B=2,C=3,D=4 (1-indexed); response==deck_choice",
    "exp2": "1=A,B=2,C=3,D=4 (1-indexed); response==deck_choice",
}


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD — `cd` into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      all exp: participant_id, source_subject, trial, response, deck_choice, win, loss, study
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _mean_net_score_by_participant(df: pd.DataFrame) -> pd.DataFrame:
    """Net advantageous-choice score (C+D minus A+B) per participant per block of 10 trials.
    response is deck chosen but 1-indexed (1=A,2=B,3=C,4=D)."""
    df = df.copy()
    df["block"] = df["trial"] // 10
    df["netscore"] = df["response"].isin([3, 4]).astype(int) - df["response"].isin([1, 2]).astype(int)
    return df.groupby(["participant_id", "block"])["netscore"].sum().reset_index()


def check_igt_learning_net_score_increase(data: dict[str, pd.DataFrame]) -> dict:
    """\"Participants ... began the task with a loan of +2000 ... [the] net outcome of 10 cards
    from the bad decks ... is -250, and +250 in the case of the good decks ... good decks become
    gradually better, whereas the bad decks become gradually worse\" — Steingroever et al. 2015,
    p.3, Methods (the pooled healthy IGT data should show the classic learning effect: net
    advantageous-choice score rises from the first to the final block)."""
    df = data["exp1"]
    p = _mean_net_score_by_participant(df)
    first = p[p.block == p.block.min()].set_index("participant_id")
    last = p[p.block == p.block.max()].set_index("participant_id")
    common = first.index.intersection(last.index)
    early, late = first.loc[common, "netscore"], last.loc[common, "netscore"]
    diff = late - early
    t, pval = stats.ttest_rel(late, early)
    effect_size = diff.mean()
    original_effect_size = np.nan
    reproduced = bool(diff.mean() > 0 and pval < 0.05)
    return {
        "effect_name": "igt_learning_net_score_increase",
        "experiment": "exp1",
        "original_effect_size": float(original_effect_size) if not np.isnan(original_effect_size) else np.nan,
        "effect_size": float(effect_size),
        "t": float(t),
        "p": float(pval),
        "early_block_mean": float(early.mean()),
        "late_block_mean": float(late.mean()),
        "reproduced": reproduced,
    }


def check_igt_learning_advantageous_late_blocks(data: dict[str, pd.DataFrame]) -> dict:
    """Pooled healthy data benchmark: by the final blocks, participants prefer advantageous decks
    (C/D) over disadvantageous ones, so the mean net score in the last block is significantly
    positive — \"The IGT is arguably the most popular neuropsychological paradigm to measure
    decision-making deficits\" — Steingroever et al. 2015, p.2, Overview (headline benchmark for
    the 'super control group')."""
    df = data["exp1"]
    p = _mean_net_score_by_participant(df)
    last = p[p.block == p.block.max()]["netscore"]
    t, pval = stats.ttest_1samp(last, 0)
    mean = last.mean()
    original_effect_size = np.nan
    reproduced = bool(mean > 0 and pval < 0.05)
    return {
        "effect_name": "igt_learning_advantageous_late_blocks",
        "experiment": "exp1",
        "original_effect_size": float(original_effect_size) if not np.isnan(original_effect_size) else np.nan,
        "effect_size": float(mean),
        "t": float(t),
        "p": float(pval),
        "n": int(len(last)),
        "reproduced": reproduced,
    }


EFFECTS = [check_igt_learning_net_score_increase, check_igt_learning_advantageous_late_blocks]


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
        print(f"{exp}: {sources[exp]}" if exp in sources else f"{exp}: (default — local ./{exp}.csv)")
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