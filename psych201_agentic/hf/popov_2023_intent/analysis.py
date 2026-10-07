# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Popov & Dames (2023), "Intent Matters:
Resolving the Intentional vs Incidental Learning Paradox in Episodic Long-term Memory"
(JEP: General), against any dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- mixed_list_intent_advantage (exp0, exp1, exp2, exp5 = reported Experiments 1-4):
  in mixed-list within-subject designs, free-recall probability is higher for
  intentionally-remembered items than for process-only (incidental) items; tested as a
  within-subject paired t-test on per-participant mean recall, expected Remember > Process.
- pure_list_no_intent_advantage (exp6 = reported Experiment 9): in a pure-list
  between-subject design, free recall for the intentional (remember_all) learning group
  does not differ from the incidental (process_all) group; tested as an independent-samples
  t-test, expected no significant difference.
"""
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0", "exp1", "exp2", "exp5", "exp6"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD.

    Required columns per experiment:
      exp0/1/2/5: participant_id, phase, trial_condition, correct
      exp6: participant_id, phase, btw_cond, trial_condition, correct, block
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _excluded(df: pd.DataFrame) -> pd.Series:
    """Per-participant excluded rows following the paper: used an aid (use_help=='Yes')
    or expected the test (expect_test=='yes'). Also honors any source 'exclude' True flag."""
    idx = df.index
    ex = pd.Series(False, index=idx)
    if "exclude" in df.columns:
        ex = ex | df["exclude"].astype(str).str.contains("True", case=False, na=False)
    if "use_help" in df.columns:
        ex = ex | df["use_help"].eq("Yes")
    if "expect_test" in df.columns:
        ex = ex | df["expect_test"].astype(str).eq("yes")
    return ex


MIXED_EXPS = ["exp0", "exp1", "exp2", "exp5"]


def check_mixed_list_intent_advantage(data: dict[str, pd.DataFrame]) -> dict:
    """\"In contrast to previous between-subject studies ... we found a substantial effect
    of intentional remembering on free recall, despite deep processing of all stimuli.\"
    — Popov & Dames 2023, p.9, Experiment 1 Results (replicated in Exp 2-4)."""
    # Per-participant recall for remember vs process across all four mixed-list experiments
    rows = []
    for exp in MIXED_EXPS:
        df = data[exp]
        st = df[df["phase"] == "study"].copy()
        st = st[~_excluded(st)]
        st = st[st["correct"].notna()]
        piv = st.pivot_table(
            index="participant_id", columns="trial_condition", values="correct", aggfunc="mean"
        )
        for rc in ["remember", "process"]:
            if rc not in piv:
                piv[rc] = np.nan
        piv = piv.dropna(subset=["remember", "process"])
        piv["diff"] = piv["remember"] - piv["process"]
        piv["experiment"] = exp
        rows.append(piv[["experiment", "remember", "process", "diff"]])
    pooled = pd.concat(rows)
    t, p = stats.ttest_rel(pooled["remember"], pooled["process"])
    effect = pooled["diff"].mean()
    reproduced = bool(pooled["diff"].mean() > 0 and p < 0.05)
    return {
        "effect_name": "mixed_list_intent_advantage",
        "experiment": ",".join(MIXED_EXPS),
        "original_effect_size": 0.283,  # Exp1: 31.0% - 2.7% = 28.3pp remember-process
        "effect_size": float(effect),
        "p": float(p),
        "n_participants": int(len(pooled)),
        "note": f"pooled across {len(MIXED_EXPS)} mixed-list exps; t={t:.2f}, p={p:.2e}",
        "reproduced": reproduced,
    }


def check_pure_list_no_intent_advantage(data: dict[str, pd.DataFrame]) -> dict:
    """\"We ... found that free recall performance did not differ overall between the
    incidental learning group (M = 16.6%) and the intentional learning group (M = 16.3%)\"
    — Popov & Dames 2023, p.30, Experiment 9 Results."""
    df = data["exp6"]
    st = df[df["phase"] == "study"].copy()
    st = st[~_excluded(st)]
    st = st[st["correct"].notna()]
    st = st[st["btw_cond"] != "remember_6"]  # pilot/other group, excluded by the paper
    st["listid"] = st["block"] + 1
    # incidental group produced a surprise recall only on List 3 (paper's main comparison)
    keep = (st["btw_cond"] != "process_all") | (st["btw_cond"] == "process_all") & (st["listid"] == 3)
    st = st[keep]
    g = st.groupby(["participant_id", "btw_cond"])["correct"].mean().reset_index()
    int_ = g.loc[g["btw_cond"] == "remember_all", "correct"]
    inc_ = g.loc[g["btw_cond"] == "process_all", "correct"]
    t, p = stats.ttest_ind(int_, inc_)
    effect = float(int_.mean() - inc_.mean())
    reproduced = bool(p >= 0.05)  # null effect reproduced: groups do not differ
    return {
        "effect_name": "pure_list_no_intent_advantage",
        "experiment": "exp6",
        "original_effect_size": -0.003,  # 16.3 - 16.6 (paper), ~0
        "effect_size": float(round(effect, 4)),
        "p": float(p),
        "n_intentional": int(len(int_)),
        "n_incidental": int(len(inc_)),
        "note": "intentional vs incidental not significantly different in pure-list design",
        "reproduced": reproduced,
    }


EFFECTS = [check_mixed_list_intent_advantage, check_pure_list_no_intent_advantage]


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
    print(f"{'effect':<{w}}  {'exp':<6}  {'orig':>10}  {'this':>10}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {str(r['experiment']):<6}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()
