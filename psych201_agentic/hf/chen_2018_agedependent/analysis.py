# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Chen et al. (2018) "Age-dependent
Pavlovian biases influence motor decision-making" (PLOS Computational Biology)
against any dataset in the Psych-301 unified schema.

Effects tested:
- reward_approach_bias (exp0): Logistic regression of gamble choice on winscore
  within reward trials; positive coefficient (higher reward -> more gambling).
- age_decline_gamble_reward (exp0): Linear regression of per-participant gamble
  proportion (reward trials) on age, controlling for gender and education;
  negative age coefficient (older adults gamble less).
- age_increase_suboptimality_reward (exp0): Linear regression of per-participant
  suboptimal-choice proportion (reward trials) on age, controlling for gender
  and education; positive age coefficient (older adults deviate more from
  optimal choices).
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
import statsmodels.api as sm

EXPERIMENTS = ["exp0", "exp1"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _partial_corr_r(y, x, covars):
    """Compute partial correlation r(y, x | covars)."""
    n = len(y)
    X_cov = sm.add_constant(covars)
    res_y = sm.OLS(y, X_cov).fit().resid
    res_x = sm.OLS(x, X_cov).fit().resid
    r = np.corrcoef(res_y, res_x)[0, 1]
    return r


def check_reward_approach_bias(data: dict[str, pd.DataFrame]) -> dict:
    """"We found that motor decision-making was subject to Pavlovian influences"
    — Chen et al. 2018, p.2, Abstract."""
    df = data["exp0"]
    valid = df[df["valid"] == 1].copy()
    reward = valid[valid["RPscore"] > 0].copy()
    X = sm.add_constant(reward[["winscore"]])
    y = reward["response"]
    model = sm.Logit(y, X).fit(disp=0, maxiter=200)
    coef = float(model.params["winscore"])
    p_val = float(model.pvalues["winscore"])
    # Compute effect size as Cohen's d from z = coef/se
    z_val = coef / model.bse["winscore"]
    d_val = z_val / np.sqrt(len(reward))
    return {
        "effect_name": "reward_approach_bias",
        "experiment": "exp0",
        "original_effect_size": 0.1042,  # difference in gamble rate 100 vs 20 (0.822 - 0.718)
        "effect_size": round(float(reward[reward["winscore"] == 100]["response"].mean() - reward[reward["winscore"] == 20]["response"].mean()), 4),
        "reproduced": bool(p_val < 0.05 and coef > 0),
        "p_value": round(p_val, 6),
        "coefficient": round(coef, 4),
    }


def check_age_decline_gamble_reward(data: dict[str, pd.DataFrame]) -> dict:
    """"We found a significant decrease in the proportion of trials in which
    participants chose to gamble across the lifespan in reward trials
    (r = -0.186, 95%CI = [-0.198, -0.175], p<0.001)"
    — Chen et al. 2018, p.6, Results / Fig 3A."""
    df = data["exp0"]
    valid = df[df["valid"] == 1].copy()
    reward = valid[valid["RPscore"] > 0].copy()
    pp = reward.groupby("participant_id").agg(
        gamble_rate=("response", "mean"),
        age=("age", "first"),
        gender=("gender", "first"),
        education=("education", "first"),
    ).reset_index()
    pp["gender_m"] = (pp["gender"] == "m").astype(int)
    X = sm.add_constant(pp[["age", "gender_m", "education"]])
    y = pp["gamble_rate"]
    model = sm.OLS(y, X).fit()
    coef = float(model.params["age"])
    p_val = float(model.pvalues["age"])
    partial_r = _partial_corr_r(y, pp["age"], pp[["gender_m", "education"]])
    return {
        "effect_name": "age_decline_gamble_reward",
        "experiment": "exp0",
        "original_effect_size": -0.186,
        "effect_size": round(partial_r, 3),
        "reproduced": bool(p_val < 0.05 and coef < 0),
        "p_value": round(p_val, 6),
        "coefficient": round(coef, 4),
    }


def check_age_increase_suboptimality_reward(data: dict[str, pd.DataFrame]) -> dict:
    """"In reward trials, there was progressive deviation from optimality across
    the lifespan (r = 0.258, 95%CI = [0.245,0.270], p<0.001)"
    — Chen et al. 2018, p.7, Results / Fig 3D."""
    df = data["exp0"]
    valid = df[df["valid"] == 1].copy()

    gambled = valid[valid["response"] == 1].copy()
    psuccess = gambled.groupby(["age_group", "screen_size", "level"])["outcome"].apply(
        lambda x: (x == 1).mean()
    ).reset_index()
    psuccess.columns = ["age_group", "screen_size", "level", "Psuccess"]

    d = valid.merge(psuccess, on=["age_group", "screen_size", "level"], how="left")
    reward_mask = d["RPscore"] > 0
    punish_mask = d["RPscore"] < 0
    d["EVgamble"] = 0.0
    d.loc[reward_mask, "EVgamble"] = d.loc[reward_mask, "Psuccess"] * d.loc[reward_mask, "winscore"]
    d.loc[punish_mask, "EVgamble"] = (1 - d.loc[punish_mask, "Psuccess"]) * d.loc[punish_mask, "losescore"]
    d["EVcertain"] = d["skipscore"]
    d["optimal_gamble"] = (d["EVgamble"] > d["EVcertain"]).astype(int)
    d["suboptimal"] = (d["response"] != d["optimal_gamble"]).astype(int)
    d = d[d["EVgamble"] != d["EVcertain"]].copy()

    reward_opt = d[reward_mask & (d["EVgamble"] != d["EVcertain"])].copy()
    pp = reward_opt.groupby("participant_id").agg(
        suboptimal=("suboptimal", "mean"),
        age=("age", "first"),
        gender=("gender", "first"),
        education=("education", "first"),
    ).reset_index()
    pp["gender_m"] = (pp["gender"] == "m").astype(int)
    X = sm.add_constant(pp[["age", "gender_m", "education"]])
    y = pp["suboptimal"]
    model = sm.OLS(y, X).fit()
    coef = float(model.params["age"])
    p_val = float(model.pvalues["age"])
    partial_r = _partial_corr_r(y, pp["age"], pp[["gender_m", "education"]])
    return {
        "effect_name": "age_increase_suboptimality_reward",
        "experiment": "exp0",
        "original_effect_size": 0.258,
        "effect_size": round(partial_r, 3),
        "reproduced": bool(p_val < 0.05 and coef > 0),
        "p_value": round(p_val, 6),
        "coefficient": round(coef, 4),
    }


EFFECTS = [
    check_reward_approach_bias,
    check_age_decline_gamble_reward,
    check_age_increase_suboptimality_reward,
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


if __name__ == "__main__":
    main()