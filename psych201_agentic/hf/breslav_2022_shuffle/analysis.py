# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Breslav et al. (2022) "Shuffle the Decks"
against any dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- age_trial_interaction (exp0): Mixed-effects logistic regression of choose_adv ~ trial * age.
  Expected: negative interaction coefficient (older children learn less).
- deplete_replenish_bias (exp0): Within the low-Theta (deplete-replenish) tertile,
  P(switch|win) > P(switch|loss) via paired t-test.
  Expected: positive mean difference, p < .05.
- age_effect_dr_only (exp0): Negative age:trial interaction on choose_adv is significant
  only in the deplete-replenish group, not in the other groups combined.
  Expected: dr_group coeff < 0 & p < .05, other groups not (coeff >= 0 or p >= .05).
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

EXPERIMENTS = ["exp0"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _fit_logit_choice(df: pd.DataFrame) -> dict:
    """Fit GLM logit: choose_adv ~ trial_scaled * age. Return coef + p for interaction."""
    X = df[["trial_scaled", "age"]].copy()
    X["trial_x_age"] = X["trial_scaled"] * X["age"]
    X = sm.add_constant(X)
    y = df["choose_adv"]
    model = sm.GLM(y, X, family=sm.families.Binomial()).fit(disp=False)
    return {"coef": float(model.params["trial_x_age"]), "p": float(model.pvalues["trial_x_age"])}


def _compute_theta(sub_df: pd.DataFrame) -> float:
    """Per-subject Theta = P(switch|loss) - P(switch|win)."""
    sub = sub_df.dropna(subset=["switch", "last_trial_win"])
    if len(sub) < 5:
        return np.nan
    p_win = sub.loc[sub["last_trial_win"] == 1, "switch"].mean()
    p_loss = sub.loc[sub["last_trial_win"] == -1, "switch"].mean()
    return p_loss - p_win


def check_age_trial_interaction(data: dict[str, pd.DataFrame]) -> dict:
    """The significant main effect of trial showed that the children successfully learned to choose the advantageous deck over time; however, there was also a significant negative interaction between age and trial — Breslav 2022, p. 4, Results."""
    df = data["exp0"].copy()
    df["trial_scaled"] = df["trial"] / 50.0
    result = _fit_logit_choice(df)
    reproduced = bool((result["coef"] < 0) and (result["p"] < 0.05))
    return {
        "effect_name": "age_trial_interaction",
        "experiment": "exp0",
        "original_effect_size": float("nan"),
        "effect_size": result["coef"],
        "p_value": result["p"],
        "reproduced": reproduced,
    }


def check_deplete_replenish_bias(data: dict[str, pd.DataFrame]) -> dict:
    """Deplete-replenish bias: a tendency to shift choices after positive outcomes and repeat choices after negative outcomes — Breslav 2022, p. 1, Abstract."""
    df = data["exp0"].copy()
    theta = df.groupby("participant_id").apply(_compute_theta, include_groups=False).dropna()
    low_cut = theta.quantile(1 / 3)
    dr_pids = set(theta.index[theta <= low_cut].tolist())
    dr_df = df[df["participant_id"].isin(dr_pids)].dropna(subset=["switch", "last_trial_win"])
    per_p = dr_df.groupby("participant_id").apply(
        lambda s: pd.Series({
            "p_win": s.loc[s["last_trial_win"] == 1, "switch"].mean(),
            "p_loss": s.loc[s["last_trial_win"] == -1, "switch"].mean(),
        }), include_groups=False
    ).dropna()
    t_stat, p_val = stats.ttest_rel(per_p["p_win"], per_p["p_loss"], alternative="greater")
    mean_diff = float(per_p["p_win"].mean() - per_p["p_loss"].mean())
    reproduced = bool((mean_diff > 0) and (p_val < 0.05))
    return {
        "effect_name": "deplete_replenish_bias",
        "experiment": "exp0",
        "original_effect_size": float("nan"),
        "effect_size": mean_diff,
        "p_value": float(p_val),
        "n_dr_group": int(len(dr_pids)),
        "reproduced": reproduced,
    }


def check_age_effect_dr_only(data: dict[str, pd.DataFrame]) -> dict:
    """Within the deplete-replenish-bias group, age was negatively associated with learning. When we modeled learning for all other children (no-bias and abundance-bias groups), age was no longer negatively associated with learning — Breslav 2022, p. 9, Results."""
    df = data["exp0"].copy()
    df["trial_scaled"] = df["trial"] / 50.0
    theta = df.groupby("participant_id").apply(_compute_theta, include_groups=False).dropna()
    low_cut = theta.quantile(1 / 3)
    dr_pids = set(theta.index[theta <= low_cut].tolist())
    other_pids = set(theta.index[theta > low_cut].tolist())
    dr_res = _fit_logit_choice(df[df["participant_id"].isin(dr_pids)])
    other_res = _fit_logit_choice(df[df["participant_id"].isin(other_pids)])
    dr_ok = bool((dr_res["coef"] < 0) and (dr_res["p"] < 0.05))
    other_ok = bool((other_res["coef"] < 0) and (other_res["p"] < 0.05))
    reproduced = dr_ok and not other_ok
    return {
        "effect_name": "age_effect_dr_only",
        "experiment": "exp0",
        "original_effect_size": float("nan"),
        "effect_size": dr_res["coef"],
        "dr_coef": dr_res["coef"],
        "dr_p": dr_res["p"],
        "other_coef": other_res["coef"],
        "other_p": other_res["p"],
        "reproduced": reproduced,
    }


EFFECTS = [check_age_trial_interaction, check_deplete_replenish_bias, check_age_effect_dr_only]


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
        print(f"{exp}: {sources.get(exp, '(default — local ./{exp}.csv)')}")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    header = f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  reproduced"
    print(header)
    print("-" * len(header))
    for r in results:
        orig = r.get("original_effect_size", float("nan"))
        this = r.get("effect_size", float("nan"))
        if np.isnan(orig):
            orig_str = "       nan"
        else:
            orig_str = f"{orig:>10.3f}"
        if np.isnan(this):
            this_str = "       nan"
        else:
            this_str = f"{this:>10.3f}"
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  {orig_str}  {this_str}  {'YES' if r['reproduced'] else 'NO'}")
        if "dr_coef" in r:
            print(f"  ├─ DR group:      β={r['dr_coef']:.4f}, p={r['dr_p']:.4f}")
            print(f"  └─ Other groups:  β={r['other_coef']:.4f}, p={r['other_p']:.4f}")
        if "p_value" in r and "dr_coef" not in r:
            print(f"   p={r['p_value']:.4f}")
        if "n_dr_group" in r:
            print(f"   n_dr_group={r['n_dr_group']}")


if __name__ == "__main__":
    main()