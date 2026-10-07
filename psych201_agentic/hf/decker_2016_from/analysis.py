# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Decker et al. (2016) "From Creatures of
Habit to Goal-Directed Learners: Tracking the Developmental Emergence of Model-Based
Reinforcement Learning" against any dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- model_free_all_groups (exp0): Main effect of previous reward on first-stage stay
  probability — logistic regression coefficient. Expected: positive and p < .05 in
  children, adolescents, and adults.
- model_based_development (exp0): The reward-by-transition-type interaction (model-based
  effect) on first-stage stay. Expected: NOT significant (p >= .05) in children,
  significant (p < .05) in adolescents and adults.
- model_based_age_increase (exp0): The model-based effect (reward-by-transition-type
  interaction) increases with age — significant positive reward-by-transition-by-age
  interaction in the full-cohort logistic regression.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats as sp_stats
from statsmodels.formula.api import logit

EXPERIMENTS = ["exp0"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _prepare_stay_data(df: pd.DataFrame) -> pd.DataFrame:
    """Build one row per stage1 paper-trial with stay/switch, previous reward,
    previous transition type, and demographic info. Follows the paper's analysis
    approach: uses only valid, non-forced stage1 trials (after the first)."""
    s1 = df[df["stage"] == "stage1"].copy()
    s2 = df[df["stage"] == "stage2"].copy()

    merged = s1.merge(
        s2[["participant_id", "block", "reward", "trans"]],
        on=["participant_id", "block"],
        suffixes=("", "_prev"),
    )
    merged = merged.sort_values(["participant_id", "trial"]).reset_index(drop=True)

    merged["prev_reward"] = merged.groupby("participant_id")["reward_prev"].shift(1)
    merged["prev_trans_binary"] = (merged.groupby("participant_id")["trans_prev"].shift(1) == "common").astype(int)
    prev_resp = merged.groupby("participant_id")["response"].shift(1)
    merged["stay"] = (merged["response"] == prev_resp).astype(int)

    merged = merged.dropna(subset=["prev_reward", "prev_trans_binary", "stay"])
    merged = merged[merged["valid"] == 1]
    return merged


def check_model_free_all_groups(data: dict[str, pd.DataFrame]) -> dict:
    """\"Children (p = .0006), adolescents (p = .0066), and adults (p < 1 x 10^-5) all showed a main effect of reward\" — Decker et al., p.852, Results."""
    df = _prepare_stay_data(data["exp0"])
    results = {}
    all_reproduced = True
    for grp in ["children", "adolescents", "adults"]:
        sub = df[df["age_group"] == grp].copy()
        if len(sub) < 10:
            results[grp] = {"coef": np.nan, "p": np.nan, "n": len(sub)}
            all_reproduced = False
            continue
        m = logit("stay ~ prev_reward", data=sub).fit(disp=0, maxiter=200)
        coef = m.params["prev_reward"]
        p = m.pvalues["prev_reward"]
        results[grp] = {"coef": coef, "p": p, "n": len(sub)}
        if p >= 0.05 or coef <= 0:
            all_reproduced = False
    avg_coef = np.mean([r["coef"] for r in results.values() if not np.isnan(r["coef"])])
    return {
        "effect_name": "model_free_all_groups",
        "experiment": "exp0",
        "original_effect_size": 0.30,
        "effect_size": float(avg_coef) if not np.isnan(avg_coef) else 0.0,
        "reproduced": all_reproduced,
        "details": results,
    }


def check_model_based_development(data: dict[str, pd.DataFrame]) -> dict:
    """\"Adolescents (p = .0016) and adults (p < .0001), but not children (p = .65), showed a reward-by-transition-type interaction effect\" — Decker et al., p.852, Results."""
    df = _prepare_stay_data(data["exp0"])
    results = {}
    all_correct = True
    for grp in ["children", "adolescents", "adults"]:
        sub = df[df["age_group"] == grp].copy()
        if len(sub) < 10:
            results[grp] = {"coef": np.nan, "p": np.nan, "n": len(sub)}
            all_correct = False
            continue
        m = logit("stay ~ prev_reward * prev_trans_binary", data=sub).fit(disp=0, maxiter=200)
        ix_coef = m.params.get("prev_reward:prev_trans_binary",
                              m.params.get("prev_trans_binary:prev_reward", np.nan))
        ix_p = m.pvalues.get("prev_reward:prev_trans_binary",
                            m.pvalues.get("prev_trans_binary:prev_reward", 1.0))
        results[grp] = {"interaction_coef": ix_coef, "p": ix_p, "n": len(sub)}
        if grp == "children":
            if ix_p < 0.05:
                all_correct = False
        else:
            if ix_p >= 0.05 or np.isnan(ix_coef) or ix_coef <= 0:
                all_correct = False
    avg_ix = np.mean([r["interaction_coef"] for g, r in results.items()
                      if g != "children" and not np.isnan(r["interaction_coef"])])
    return {
        "effect_name": "model_based_development",
        "experiment": "exp0",
        "original_effect_size": 0.35,
        "effect_size": float(avg_ix) if not np.isnan(avg_ix) else 0.0,
        "reproduced": all_correct,
        "details": results,
    }


def check_model_based_age_increase(data: dict[str, pd.DataFrame]) -> dict:
    """\"Only the model-based learning signature exhibited a significant increase with age (a reward-by-transition-type-by-age interaction, p = .0004)\" — Decker et al., p.852, Results."""
    df = _prepare_stay_data(data["exp0"])
    df["age_z"] = (df["age"] - df["age"].mean()) / df["age"].std()
    m = logit("stay ~ prev_reward * prev_trans_binary * age_z", data=df).fit(disp=0, maxiter=200)
    param_names = list(m.params.index)
    ix3_name = [p for p in param_names if "prev_reward" in p and "prev_trans_binary" in p and "age_z" in p]
    if not ix3_name:
        return {
            "effect_name": "model_based_age_increase",
            "experiment": "exp0",
            "original_effect_size": 0.18,
            "effect_size": 0.0,
            "reproduced": False,
            "details": {"error": "three-way interaction term not found", "params": param_names},
        }
    ix3_name = ix3_name[0]
    coef = m.params[ix3_name]
    p = m.pvalues[ix3_name]
    reproduced = coef > 0 and p < 0.05
    return {
        "effect_name": "model_based_age_increase",
        "experiment": "exp0",
        "original_effect_size": 0.18,
        "effect_size": float(coef),
        "reproduced": reproduced,
        "details": {"coef": float(coef), "p": float(p), "n": len(df)},
    }


EFFECTS = [
    check_model_free_all_groups,
    check_model_based_development,
    check_model_based_age_increase,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
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
    for r in results:
        if "details" in r:
            print(f"  {r['effect_name']} details: {r['details']}")


if __name__ == "__main__":
    main()