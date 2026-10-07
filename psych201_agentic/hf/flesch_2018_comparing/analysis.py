# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Flesch, Balaguer, Dekker, Nili &
Summerfield (2018), "Comparing continual task learning in minds and machines",
PNAS 115(44):E10313-E10322, against any dataset in the Psych-301 unified schema
(see schema.md).

Effects tested:
- blocked_beats_interleaved_test_accuracy (exp0, Exp1a cardinal): mean test-phase
  accuracy is higher in the B200 (blocked) group than the interleaved group during
  the final interleaved no-feedback test. Direction: B200 > interleaved.
- blocked_reduces_cardinal_irrelevant_intrusion (exp0, Exp1a cardinal): on the
  cardinal rules, the task-irrelevant dimension intrudes less (shallower choice
  slope) in the B200 group than the interleaved group, evidencing factorization.
  Direction: B200 < interleaved.
- blocked_reduces_diagonal_irrelevant_intrusion (exp1, Exp1b diagonal): on the
  rotated (diagonal) rules, intrusion along the axis orthogonal to the boundary is
  smaller in the B200 group than interleaved. Direction: B200 < interleaved.
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
      exp0: participant_id, trial, phase, condition, state, response, correct,
            branch_index, leaf_index
      exp1: participant_id, trial, phase, condition, state, response, correct,
            branch_index, leaf_index
      exp2: participant_id, trial, phase, condition, state, response, correct,
            branch_index, leaf_index, x_final, y_final (rating)
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv"), low_memory=False) for exp in EXPERIMENTS}


def _per_subj_test_acc(df: pd.DataFrame) -> pd.DataFrame:
    test = df[(df["phase"] == "test") & df["response"].notna()]
    acc = test.groupby(["participant_id", "condition"])["correct"].mean()
    return acc.reset_index()


def _group_means(acc: pd.DataFrame, cond: str) -> pd.Series:
    return acc.loc[acc["condition"] == cond, "correct"]


def check_blocked_beats_interleaved_test_accuracy(data: dict[str, pd.DataFrame]) -> dict:
    """\"Firstly, the B200 group ... performed overall best during interleaved test
    (ANOVA: F3,172 = 5.06, P < 0.05; B200 > Interleaved: t93 = 2.32, P < 0.05,
    d = 0.47)\" — Flesch et al. 2018, p.E10315, Results (Exp 1a)."""
    acc = _per_subj_test_acc(data["exp0"])
    b200 = _group_means(acc, "b200")
    itl = _group_means(acc, "interleaved")
    t, p = stats.ttest_ind(b200, itl, equal_var=False)
    d = (b200.mean() - itl.mean()) / np.sqrt((b200.std() ** 2 + itl.std() ** 2) / 2)
    reproduced = bool(b200.mean() > itl.mean())
    return {
        "effect_name": "blocked_beats_interleaved_test_accuracy",
        "experiment": "exp0",
        "original_effect_size": 0.47,
        "effect_size": float(d),
        "reproduced": reproduced,
        "stats": f"t={t:.2f}, p={p:.3f}, B200={b200.mean():.3f}, Int={itl.mean():.3f}",
    }


def _intrusion_score(df: pd.DataFrame, diagonal: bool) -> pd.Series:
    """Per-participant intrusion: mean |corr(response, task-irrelevant axis)| over
    the two contexts (states) at test. For cardinal, the two raw axes are the task
    axes; irrelevant is the non-predictive axis (recovered per subject-context).
    For diagonal, the boundary lies on the leaf+branch axis, so the orthogonal
    (leaf-branch) projection is task-irrelevant."""
    test = df[(df["phase"] == "test") & df["response"].notna()]
    out = {}
    for pid, g in test.groupby("participant_id"):
        intr = []
        for ctx in g["state"].unique():
            s = g[g["state"] == ctx]
            r = s["response"].values
            if diagonal:
                ir = s["leaf_index"].values - s["branch_index"].values
                if np.std(ir) == 0:
                    continue
                intr.append(abs(np.corrcoef(r, ir)[0, 1]))
            else:
                cl = abs(np.corrcoef(r, s["leaf_index"].values)[0, 1])
                cb = abs(np.corrcoef(r, s["branch_index"].values)[0, 1])
                intr.append(min(cl, cb))
        if intr:
            out[pid] = np.mean(intr)
    return pd.Series(out)


def check_blocked_reduces_cardinal_irrelevant_intrusion(data: dict[str, pd.DataFrame]) -> dict:
    """\"...blocked learning reduced the impact of the irrelevant dimension on
    choice, as if B200 training prevented intrusions from the rival task (B200 <
    Interleaved: Z = 2.99, P < 0.01, r = 0.31)\" — Flesch et al. 2018, p.E10315,
    Results (Exp 1a)."""
    df = data["exp0"]
    intru = _intrusion_score(df, diagonal=False)
    cond = df.groupby("participant_id")["condition"].first()
    b200 = intru[cond[cond == "b200"].index].dropna()
    itl = intru[cond[cond == "interleaved"].index].dropna()
    u, p = stats.mannwhitneyu(b200, itl, alternative="less")
    n = len(b200) + len(itl)
    z = stats.norm.ppf(p)
    r = z / np.sqrt(n)
    reproduced = bool(b200.mean() < itl.mean() and p < 0.05)
    return {
        "effect_name": "blocked_reduces_cardinal_irrelevant_intrusion",
        "experiment": "exp0",
        "original_effect_size": 0.31,
        "effect_size": float(r),
        "reproduced": reproduced,
        "stats": f"U p={p:.3f}, B200={b200.mean():.3f}, Int={itl.mean():.3f}",
    }


def check_blocked_reduces_diagonal_irrelevant_intrusion(data: dict[str, pd.DataFrame]) -> dict:
    """\"This was revealed by shallower psychometric slopes for the irrelevant
    dimension at test (B200 < Interleaved: Z = 3.11, P < 0.01, r = 0.34)\" —
    Flesch et al. 2018, p.E10316, Results (Exp 1b)."""
    df = data["exp1"]
    intru = _intrusion_score(df, diagonal=True)
    cond = df.groupby("participant_id")["condition"].first()
    b200 = intru[cond[cond == "b200"].index].dropna()
    itl = intru[cond[cond == "interleaved"].index].dropna()
    u, p = stats.mannwhitneyu(b200, itl, alternative="less")
    n = len(b200) + len(itl)
    z = stats.norm.ppf(p)
    r = z / np.sqrt(n)
    reproduced = bool(b200.mean() < itl.mean() and p < 0.05)
    return {
        "effect_name": "blocked_reduces_diagonal_irrelevant_intrusion",
        "experiment": "exp1",
        "original_effect_size": 0.34,
        "effect_size": float(r),
        "reproduced": reproduced,
        "stats": f"U p={p:.3f}, B200={b200.mean():.3f}, Int={itl.mean():.3f}",
    }


EFFECTS = [
    check_blocked_beats_interleaved_test_accuracy,
    check_blocked_reduces_cardinal_irrelevant_intrusion,
    check_blocked_reduces_diagonal_irrelevant_intrusion,
]


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
              f"{'YES' if r['reproduced'] else 'NO'}   [{r.get('stats', '')}]")


if __name__ == "__main__":
    main()
