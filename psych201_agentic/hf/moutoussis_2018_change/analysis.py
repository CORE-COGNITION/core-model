# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "scipy"]
# ///
"""Check the primary behavioral effects of Moutoussis et al. (2018) against any dataset
in the Psych-301 unified schema.

Effects tested:
- pavlovian_congruency_performance (exp0, exp1): Performance (P[correct]) is higher in
  Pavlovian-congruent (win_go, lose_nogo) than Pavlovian-incongruent (win_nogo, lose_go)
  conditions. Test: one-tailed paired t-test.
"""
from __future__ import annotations

import argparse

import pandas as pd
from scipy.stats import ttest_rel

EXPERIMENTS = ["exp0", "exp1"]


def _compute_correct(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["correct"] = 0
    go_mask = (df["condition"].isin(["win_go", "lose_go"])) & (df["response"] == 1)
    nogo_mask = (df["condition"].isin(["win_nogo", "lose_nogo"])) & (df["response"] == 0)
    df.loc[go_mask | nogo_mask, "correct"] = 1
    return df


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def check_pavlovian_congruency_performance(data: dict[str, pd.DataFrame]) -> dict:
    """\"The characteristic 'Pavlovian bias' interaction pattern was seen, with
    Pavlovian-incongruent conditions showing worse performance than the corresponding
    congruent ones (Go to Win > NoGo to Win, NoGo to Avoid Loss > Go to Avoid Loss)
    at all stages.\" — Moutoussis et al. 2018, p.7, 'Large naturalistic study'."""
    results = []
    for exp_name in EXPERIMENTS:
        df = _compute_correct(data[exp_name])
        df = df[df["valid"] == 1]
        subj_acc = df.groupby(["participant_id", "condition"])["correct"].mean().reset_index()
        congruent = subj_acc[subj_acc["condition"].isin(["win_go", "lose_nogo"])]
        incongruent = subj_acc[subj_acc["condition"].isin(["win_nogo", "lose_go"])]
        merged = congruent.merge(
            incongruent, on="participant_id", suffixes=("_cong", "_incong")
        )
        t_stat, p_val = ttest_rel(
            merged["correct_cong"], merged["correct_incong"], alternative="greater"
        )
        n = len(merged)
        d = t_stat / (n ** 0.5)
        mean_congruent = merged["correct_cong"].mean()
        mean_incongruent = merged["correct_incong"].mean()
        results.append({
            "effect_name": "pavlovian_congruency_performance",
            "experiment": exp_name,
            "original_effect_size": 0.18,
            "effect_size": float(mean_congruent - mean_incongruent),
            "t_stat": float(t_stat),
            "p_value": float(p_val),
            "cohens_d": float(d),
            "reproduced": bool(p_val < 0.05 and mean_congruent > mean_incongruent),
        })
    return results


EFFECTS = [check_pavlovian_congruency_performance]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    data = load_data(sources)
    results = []
    for fn in EFFECTS:
        res = fn(data)
        if isinstance(res, list):
            results.extend(res)
        else:
            results.append(res)
    return results


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
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{r['p_value']:>10.4f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()