# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Pugacheva & Günther (2024), "Lexical choice
and word formation in a taboo game paradigm", JML, against any dataset in the Psych-301
unified schema (see schema.md).

Effects tested:
- existing_closer_than_novel (exp0, Experiment 1): existing-word taboo responses are
  semantically closer to the target word than novel responses (lower fastText
  neighbourhood rank / higher cosine); two-sample test between existence groups.
- existing_closer_than_novelcompound (exp1, Experiment 2): replication of Exp 1 — existing
  words are represented closer to the target than novel-compound responses.
- novel_compound_guess_advantage (exp2, Experiment 3): new raters guess the correct original
  target and rate the fit higher for novel-compound responses than for existing-word
  responses.
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
      exp0: participant_id, trial, stimulus, response, cosine, existence, rank, centroid
      exp1: participant_id, trial, stimulus, response, cosine, existence, rank, centroid, condition
      exp2: participant_id, block, stimulus, existence, original_target, response, rating, correct_guess
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _closeness_comparison(df: pd.DataFrame, novel_mask) -> tuple[float, float, float, bool]:
    """Shared two-sample test: are existing-word responses closer (lower log rank) to the
    target than novel(-compound) responses? Returns (cohens_d, p, delta_lrank, reproduced)."""
    lr = np.log(df["rank"])
    existing = lr[~novel_mask]
    novel = lr[novel_mask]
    t, p = stats.ttest_ind(existing, novel, equal_var=False)
    n1, n2 = len(existing), len(novel)
    n = n1 + n2
    d = t * np.sqrt(1.0 / n1 + 1.0 / n2)
    delta = existing.mean() - novel.mean()
    reproduced = bool(not (np.isnan(t) or np.isnan(p)) and delta < 0 and p < 0.05)
    return float(d), float(p), float(delta), reproduced


def check_existing_closer_than_novel(data: dict[str, pd.DataFrame]) -> dict:
    """\"existing words were represented closer than novel words\" — Pugacheva & Günther
    (2024), Abstract; and existing words "represented significantly closer to the targets
    than the free associates", p.21, Experiment 1 Results."""
    df = data["exp0"]
    novel_mask = df["existence"].astype(str).str.lower().str.contains("novel")
    d, p, delta, reproduced = _closeness_comparison(df, novel_mask)
    return {
        "effect_name": "existing_closer_than_novel",
        "experiment": "exp0",
        "original_effect_size": 5891.67,
        "effect_size": d,
        "p": p,
        "delta_log_rank": delta,
        "reproduced": reproduced,
    }


def check_existing_closer_than_novelcompound(data: dict[str, pd.DataFrame]) -> dict:
    """\"existing words were represented significantly closer to the targets than the free
    associates\" (Exp 1) and 'The results replicated the pattern observed in Experiment 1'
    — Pugacheva & Günther 2024, p.21 & p.26, Experiment 2 Results."""
    df = data["exp1"]
    novel_mask = df["existence"].astype(str).str.lower().str.contains("novel")
    d, p, delta, reproduced = _closeness_comparison(df, novel_mask)
    return {
        "effect_name": "existing_closer_than_novelcompound",
        "experiment": "exp1",
        "original_effect_size": 5891.67,
        "effect_size": d,
        "p": p,
        "delta_log_rank": delta,
        "reproduced": reproduced,
    }


def check_novel_compound_guess_advantage(data: dict[str, pd.DataFrame]) -> dict:
    """\"...for novel compound responses as compared to existing word responses\" people are
    more likely to guess the correct original word, with 'far more correct guesses for novel
    compounds than existing words' — Pugacheva & Günther 2024, Abstract & p.36, Exp 3 Results."""
    df = data["exp2"]
    bdf = df.drop_duplicates(["participant_id", "block"])
    ex = bdf["existence"].astype(str).str.lower().str.replace(" ", "", regex=False)
    nc = ex == "novelcompound"
    existing = ex == "existing"
    acc_a = bdf.loc[nc, "correct_guess"]
    acc_b = bdf.loc[existing, "correct_guess"]
    t_acc, p_acc = stats.ttest_ind(acc_a, acc_b, equal_var=False)
    n1, n2 = len(acc_a), len(acc_b)
    d_acc = t_acc * np.sqrt(1.0 / n1 + 1.0 / n2)
    reproduced = bool(not (np.isnan(t_acc) or np.isnan(p_acc))
                      and acc_a.mean() > acc_b.mean() and p_acc < 0.05)
    return {
        "effect_name": "novel_compound_guess_advantage",
        "experiment": "exp2",
        "original_effect_size": None,
        "effect_size": d_acc,
        "p": float(p_acc),
        "delta_accuracy": float(acc_a.mean() - acc_b.mean()),
        "accuracy": {"novel_compound": float(acc_a.mean()),
                     "existing": float(acc_b.mean())},
        "reproduced": reproduced,
    }


EFFECTS = [
    check_existing_closer_than_novel,
    check_existing_closer_than_novelcompound,
    check_novel_compound_guess_advantage,
]


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
    print(f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'d':>10}  {'p':>8}  reproduced")
    for r in results:
        orig = r["original_effect_size"]
        os_ = "--" if orig is None else f"{orig:.3f}"
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  {os_:>10}  "
              f"{r['effect_size']:>10.3f}  {r['p']:>8.3g}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()