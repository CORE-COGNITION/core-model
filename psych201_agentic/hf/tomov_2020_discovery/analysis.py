# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Tomov, Tastan, Dugan, & Gershman (2020),
"Hierarchical inference and the emergence of structure in human mental representations
can be incorporated into a generalized theory of planning" (PLOS Computational Biology)
against any dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- exp1_hierarchy_discovery_first_move (exp0): On the Experiment-1 test trial (6->1, path
  length 2) participants prefer a FIRST MOVE to state 5 over state 7; measured as the
  proportion of test-trial first moves to 5 vs. chance 0.5, two-tailed binomial test.
- exp2_bad_gt_control (exp1): In Experiment 2, on the test trial the "bad"-clusters
  condition prefers the suboptimal move 6->5 (binomial vs. 0.5) significantly more than
  the control condition (chi-square test of independence of proportions).
- exp4_fullmap_hierarchy_discovery (exp3): Experiment 4 (fully visible graph) test-trial
  first move 6->5 vs. 6->7, proportion vs. chance 0.5, right-tailed binomial test.
- exp5_bad_worse_than_controls (exp4): Experiment 5 (full map, subway9) "bad" condition
  performs worse (higher move-to-5 fraction on the test trial) than control1/control2
  (chi-square tests of independence).
- exp7_rewards_cluster_route (exp5): Experiment 7 (reward-based clusters) test-trial
  6->1 first move prefers state 5 over 7 (route with fewer reward-cluster boundaries),
  proportion vs. chance 0.5, two-tailed binomial test.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0", "exp1", "exp3", "exp4", "exp5"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD — `cd` into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      exp0: participant_id, start, goal, path, phase, length, response
      exp1: participant_id, condition, start, goal, path, phase, length, response
      exp3: participant_id, start, goal, path, phase, length, response
      exp4: participant_id, condition, start, goal, path, phase, length, response
      exp5: participant_id, start, goal, path, phase, length, response
    """
    sources = sources or {}
    data = {}
    for exp in EXPERIMENTS:
        path = sources.get(exp, f"./{exp}.csv")
        try:
            data[exp] = pd.read_csv(path)
        except FileNotFoundError:
            data[exp] = None
    return data


def _test_trial_first_moves(df: pd.DataFrame) -> pd.Series:
    """Returns, one per participant, the first-move response (5 or 7) on the single
    6->1 test trial (start=6, goal=1, 2-node path)."""
    sub = df[(df["start"] == 6) & (df["goal"] == 1) & (df["length"] == 2)]
    if "phase" in sub.columns:
        sub = sub[sub["phase"] == "test"]
    sub = sub[sub["response"].isin([5, 7])]
    return sub["response"]


def check_exp1_hierarchy_discovery_first_move(data: dict[str, pd.DataFrame]) -> dict:
    """\"[O]n the test trial, participants were more likely to go to state 5 than to state 7 (Fig 9B; 58 out of 87, p = 0.003, two-tailed binomial test)\" — Tomov et al. 2020, p.18, Results (Experiment one)."""
    df = data["exp0"]
    moves = _test_trial_first_moves(df)
    n5 = int((moves == 5).sum())
    total = int(moves.size)
    prop5 = n5 / total if total else np.nan
    p = stats.binomtest(n5, total, 0.5).pvalue if total else np.nan
    reproduced = bool(total > 0 and prop5 > 0.5 and p < 0.05)
    return {
        "effect_name": "exp1_hierarchy_discovery_first_move",
        "experiment": "exp0",
        "original_effect_size": 58.0 / 87.0,
        "effect_size": float(prop5),
        "n5": n5,
        "total": total,
        "p": float(p),
        "reproduced": reproduced,
    }


def check_exp2_bad_gt_control(data: dict[str, pd.DataFrame]) -> dict:
    """\"[O]n the test trial, participants preferred the suboptimal move from 6 to 5 in the 'bad' clusters condition (Fig 10B; 53 out of 78, p = 0.002 ...), significantly more than the control condition (χ2(1, 165) = 6.52, p = 0.01 ...)\" — Tomov et al. 2020, p.19-20, Results (Experiment two)."""
    df = data["exp1"]
    if df is None or "condition" not in df.columns:
        return {"effect_name": "exp2_bad_gt_control", "experiment": "exp1",
                "original_effect_size": 6.52, "effect_size": np.nan, "reproduced": False}
    sub = df[df["condition"].isin(["bad", "control"])]
    moves = _test_trial_first_moves(sub)
    tbl = moves.groupby(sub.loc[moves.index, "condition"]).value_counts().unstack().reindex(
        columns=[5, 7]).fillna(0).astype(int)
    if "bad" not in tbl.index or "control" not in tbl.index:
        return {"effect_name": "exp2_bad_gt_control", "experiment": "exp1",
                "original_effect_size": 6.52, "effect_size": np.nan, "reproduced": False}
    bad, ctl = tbl.loc["bad"], tbl.loc["control"]
    n5b, totb = int(bad[5]) + int(bad[7]), int(bad[5])
    p_binom = float(stats.binomtest(int(bad[5]), n5b, 0.5).pvalue) if n5b else np.nan
    chi2 = float(stats.chi2_contingency(np.array([bad, ctl]), correction=False)[0])
    p_chi = float(stats.chi2_contingency(np.array([bad, ctl]), correction=False)[1])
    prop_bad, prop_ctl = bad[5] / n5b, ctl[5] / (ctl[5] + ctl[7])
    reproduced = bool(n5b and prop_bad > 0.5 and p_binom < 0.05
                      and prop_bad > prop_ctl and p_chi < 0.05)
    return {
        "effect_name": "exp2_bad_gt_control",
        "experiment": "exp1",
        "original_effect_size": 6.52,
        "effect_size": chi2,
        "bad_prop5": float(prop_bad),
        "control_prop5": float(prop_ctl),
        "p_binom": p_binom,
        "p_chi": p_chi,
        "reproduced": reproduced,
    }


def check_exp4_fullmap_hierarchy_discovery(data: dict[str, pd.DataFrame]) -> dict:
    """\"[E]ven with full knowledge of the graph, participants still developed a bias (Fig 12B; 51 out of 77 participants, p = 0.0014, right-tailed binomial test)\" — Tomov et al. 2020, p.24, Results (Experiment four)."""
    df = data["exp3"]
    moves = _test_trial_first_moves(df)
    n5, total = int((moves == 5).sum()), int(moves.size)
    prop5 = n5 / total if total else np.nan
    p = stats.binomtest(n5, total, 0.5, alternative="greater").pvalue if total else np.nan
    reproduced = bool(total > 0 and prop5 > 0.5 and p < 0.05)
    return {
        "effect_name": "exp4_fullmap_hierarchy_discovery",
        "experiment": "exp3",
        "original_effect_size": 51.0 / 77.0,
        "effect_size": float(prop5),
        "n5": n5, "total": total, "p": float(p),
        "reproduced": reproduced,
    }


def check_exp5_bad_worse_than_controls(data: dict[str, pd.DataFrame]) -> dict:
    """\"[I]nducing 'bad' clusters still led to significantly worse performance on the test trial than either control condition (Fig 13B; χ2(1, 209) = 9.35, p = 0.002 for bad vs. control 1; χ2(1, 207) = 7.7, p = 0.006 for bad vs. control 2 ...)\" — Tomov et al. 2020, p.24-25, Results (Experiment five)."""
    df = data["exp4"]
    if df is None or "condition" not in df.columns:
        return {"effect_name": "exp5_bad_worse_than_controls", "experiment": "exp4",
                "original_effect_size": 9.35, "effect_size": np.nan, "reproduced": False}
    sub = df[df["condition"].isin(["bad", "control1", "control2"])]
    moves = _test_trial_first_moves(sub)
    tbl = moves.groupby(sub.loc[moves.index, "condition"]).value_counts().unstack().reindex(
        columns=[5, 7]).fillna(0).astype(int)
    if not {"bad", "control1", "control2"}.issubset(tbl.index):
        return {"effect_name": "exp5_bad_worse_than_controls", "experiment": "exp4",
                "original_effect_size": 9.35, "effect_size": np.nan, "reproduced": False}
    bad = tbl.loc["bad"]
    chi2s, ps, okdir = [], [], True
    for c in ["control1", "control2"]:
        ctl = tbl.loc[c]
        stat, p = stats.chi2_contingency(np.array([bad, ctl]), correction=False)[:2]
        chi2s.append(float(stat)); ps.append(float(p))
        okdir &= bool(bad[5] / (bad[5] + bad[7]) > ctl[5] / (ctl[5] + ctl[7]))
    reproduced = bool(okdir and all(p < 0.05 for p in ps))
    return {
        "effect_name": "exp5_bad_worse_than_controls",
        "experiment": "exp4",
        "original_effect_size": 9.35,
        "effect_size": chi2s[0],
        "chi2": chi2s,
        "ps": ps,
        "reproduced": reproduced,
    }


def check_exp7_rewards_cluster_route(data: dict[str, pd.DataFrame]) -> dict:
    """\"[P]articipants preferred the route with fewer cluster boundaries (Fig 15B; 102 out of 174 participants, p = 0.03, two-tailed binomial test)\" — Tomov et al. 2020, p.31, Results (Experiment seven)."""
    df = data["exp5"]
    moves = _test_trial_first_moves(df)
    n5, total = int((moves == 5).sum()), int(moves.size)
    prop5 = n5 / total if total else np.nan
    p = stats.binomtest(n5, total, 0.5).pvalue if total else np.nan
    reproduced = bool(total > 0 and prop5 > 0.5 and p < 0.05)
    return {
        "effect_name": "exp7_rewards_cluster_route",
        "experiment": "exp5",
        "original_effect_size": 102.0 / 174.0,
        "effect_size": float(prop5),
        "n5": n5, "total": total, "p": float(p),
        "reproduced": reproduced,
    }


EFFECTS = [check_exp1_hierarchy_discovery_first_move, check_exp2_bad_gt_control,
           check_exp4_fullmap_hierarchy_discovery, check_exp5_bad_worse_than_controls,
           check_exp7_rewards_cluster_route]


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