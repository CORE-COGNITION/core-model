# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Shahar et al. (2019) "Improving the
reliability of model-based decision-making estimates in the two-stage decision
task with reaction-times and drift-diffusion modeling" against any dataset in
the Psych-301 unified schema (see schema.md).

Effects tested:
- mb_choice_transition_reward_interaction (exp0): The transition × reward
  interaction on first-stage stay probability. Logistic regression:
  stay ~ transition * reward (paper coding: +1 common/-1 rare, +1 rewarded/-1
  unrewarded). Prediction: positive interaction coefficient (more stay after
  common+rewarded and rare+unrewarded trials).
- mb_rt_transition_effect (exp0): The transition main effect on second-stage
  RTs. Prediction: negative direction — faster RT after common transitions
  (transition main effect in mixed-model, or t-test common<rare).
- mb_choice_rt_correlation (exp0): Positive Pearson correlation between
  individual MB-I(choice) interaction coefficients and MB-II(RT) transition
  effects across participants.
"""
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, ttest_ind
from statsmodels.formula.api import logit

EXPERIMENTS = ["exp0"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _prepare_choice_data(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame with one row per first-stage trial (after the first),
    with `stay`, `prev_transition`, and `prev_reward` columns suitable for
    logistic regression.

    Paper coding of variables:
      transition: +1 = common (0 in data), -1 = rare (1 in data)
      reward:     +1 = rewarded, -1 = unrewarded
    """
    first = df[df["reward"].isna()].sort_values(
        ["participant_id", "session", "task_id", "trial"]
    ).copy()

    first["prev_response"] = first.groupby(
        ["participant_id", "session", "task_id"]
    )["response"].shift(1)
    first["stay"] = (first["response"] == first["prev_response"]).astype(int)
    first = first.dropna(subset=["prev_response"])

    first["prev_transition"] = first.groupby(
        ["participant_id", "session", "task_id"]
    )["transition"].shift(1)

    second = df[df["reward"].notna()][
        ["participant_id", "session", "task_id", "block", "reward"]
    ].rename(columns={"reward": "out_reward"})
    first = first.merge(
        second, on=["participant_id", "session", "task_id", "block"], how="left"
    )
    first["prev_reward"] = first.groupby(
        ["participant_id", "session", "task_id"]
    )["out_reward"].shift(1)
    first = first.dropna(subset=["prev_reward"])

    first["transition_c"] = (1 - 2 * first["prev_transition"]).astype(float)
    first["reward_c"] = (2 * first["prev_reward"] - 1).astype(float)
    return first


def _prepare_rt_data(df: pd.DataFrame) -> pd.DataFrame:
    second = df[df["reward"].notna()].dropna(subset=["rt"]).copy()
    second["transition_c"] = (1 - 2 * second["transition"]).astype(float)
    return second


def check_mb_choice_transition_reward_interaction(
    data: dict[str, pd.DataFrame],
) -> dict:
    """"For MB-I(choice) the transition × reward interaction factor explained 25.1%
    of the first-stage stay probability." — Shahar et al., 2019, p.7, Results."""
    df = data["exp0"]
    ch = _prepare_choice_data(df)
    if len(ch) == 0:
        return {
            "effect_name": "mb_choice_transition_reward_interaction",
            "experiment": "exp0",
            "original_effect_size": 0.251,
            "effect_size": np.nan,
            "reproduced": False,
            "notes": "no valid trials",
        }
    try:
        md = logit("stay ~ transition_c * reward_c", data=ch).fit(
            disp=0, maxiter=500
        )
        coef = md.params["transition_c:reward_c"]
        pval = md.pvalues["transition_c:reward_c"]
        pseudo_r2 = 1 - md.llf / md.llnull
        reproduced = bool(coef > 0 and pval < 0.05)
    except Exception as e:
        return {
            "effect_name": "mb_choice_transition_reward_interaction",
            "experiment": "exp0",
            "original_effect_size": 0.251,
            "effect_size": np.nan,
            "reproduced": False,
            "notes": f"model failed: {e}",
        }
    return {
        "effect_name": "mb_choice_transition_reward_interaction",
        "experiment": "exp0",
        "original_effect_size": 0.251,
        "effect_size": float(pseudo_r2),
        "coef": float(coef),
        "pval": float(pval),
        "reproduced": reproduced,
    }


def check_mb_rt_transition_effect(data: dict[str, pd.DataFrame]) -> dict:
    """For MB-II(RT), the transition factor explained 67.3% of the mean RT2
    variability." — Shahar et al., 2019, p.7, Results.
    MB-II(RT) = mean(RT2|rare) - mean(RT2|common). Model-based → positive."""
    df = data["exp0"]
    rt = _prepare_rt_data(df)
    if len(rt) == 0:
        return {
            "effect_name": "mb_rt_transition_effect",
            "experiment": "exp0",
            "original_effect_size": 0.673,
            "effect_size": np.nan,
            "reproduced": False,
            "notes": "no valid trials",
        }
    try:
        common_rt = rt.loc[rt["transition"] == 0, "rt"].mean()
        rare_rt = rt.loc[rt["transition"] == 1, "rt"].mean()
        diff = rare_rt - common_rt  # Eq 13: rare - common
        tstat, pval = ttest_ind(
            rt.loc[rt["transition"] == 1, "rt"],
            rt.loc[rt["transition"] == 0, "rt"],
            alternative="greater",
        )
        grand_mean = rt["rt"].mean()
        ss_total = ((rt["rt"] - grand_mean) ** 2).sum()
        ss_between = 0
        for val, grp in rt.groupby("transition"):
            ss_between += len(grp) * (grp["rt"].mean() - grand_mean) ** 2
        eta_sq = ss_between / ss_total if ss_total > 0 else 0
        reproduced = bool(diff > 0 and pval < 0.05)
    except Exception as e:
        return {
            "effect_name": "mb_rt_transition_effect",
            "experiment": "exp0",
            "original_effect_size": 0.673,
            "effect_size": np.nan,
            "reproduced": False,
            "notes": f"model failed: {e}",
        }
    return {
        "effect_name": "mb_rt_transition_effect",
        "experiment": "exp0",
        "original_effect_size": 0.673,
        "effect_size": float(eta_sq),
        "diff_ms": float(diff),
        "pval": float(pval),
        "reproduced": reproduced,
    }


def check_mb_choice_rt_correlation(data: dict[str, pd.DataFrame]) -> dict:
    """Results suggest a strong relationship between MB-I(choice), MB-II(RT)
    (with ~37% shared variance, see Fig 3A)" — Shahar et al., 2019, p.8,
    Results. Uses individual (non-hierarchical) scores per Eq 11 and Eq 13."""
    df = data["exp0"]
    first = df[df["reward"].isna()].sort_values(
        ["participant_id", "session", "task_id", "trial"]
    ).copy()
    second = df[df["reward"].notna()].copy()
    first["prev_response"] = first.groupby(
        ["participant_id", "session", "task_id"]
    )["response"].shift(1)
    first["stay"] = (first["response"] == first["prev_response"]).astype(int)
    first = first.dropna(subset=["prev_response"])
    first["prev_transition"] = first.groupby(
        ["participant_id", "session", "task_id"]
    )["transition"].shift(1)
    fb = second[["participant_id", "session", "task_id", "block", "reward"]].rename(
        columns={"reward": "out_reward"}
    )
    first = first.merge(
        fb, on=["participant_id", "session", "task_id", "block"], how="left"
    )
    first["prev_reward"] = first.groupby(
        ["participant_id", "session", "task_id"]
    )["out_reward"].shift(1)
    first = first.dropna(subset=["prev_reward"])
    mb_scores = []
    for (pid, sess, tid), subj in first.groupby(
        ["participant_id", "session", "task_id"]
    ):
        def sp(trans, rew):
            d = subj[(subj["prev_transition"] == trans) & (subj["prev_reward"] == rew)]["stay"]
            return d.mean() if len(d) > 0 else 0.0
        # Eq 11: P(stay|comm,rew) - P(stay|comm,unrew) - P(stay|rare,rew) + P(stay|rare,unrew)
        mb_choice = sp(0, 1.0) - sp(0, 0.0) - sp(1, 1.0) + sp(1, 0.0)
        subj_rt = second[
            (second["participant_id"] == pid)
            & (second["session"] == sess)
            & (second["task_id"] == tid)
        ].dropna(subset=["rt"])
        if len(subj_rt) < 5:
            continue
        common_m = subj_rt.loc[subj_rt["transition"] == 0, "rt"].mean()
        rare_m = subj_rt.loc[subj_rt["transition"] == 1, "rt"].mean()
        mb_rt = rare_m - common_m  # Eq 13: rare - common
        mb_scores.append((mb_choice, mb_rt))
    if len(mb_scores) < 10:
        return {
            "effect_name": "mb_choice_rt_correlation",
            "experiment": "exp0",
            "original_effect_size": 0.608,
            "effect_size": np.nan,
            "reproduced": False,
            "notes": f"too few subjects ({len(mb_scores)})",
        }
    scores = np.array(mb_scores)
    r, pval = pearsonr(scores[:, 0], scores[:, 1])
    reproduced = bool(r > 0 and pval < 0.05)
    return {
        "effect_name": "mb_choice_rt_correlation",
        "experiment": "exp0",
        "original_effect_size": 0.608,
        "effect_size": float(r),
        "r_squared": float(r ** 2),
        "pval": float(pval),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_mb_choice_transition_reward_interaction,
    check_mb_rt_transition_effect,
    check_mb_choice_rt_correlation,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None, help=f"CSV path for {exp}")
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
    print(
        f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  reproduced"
    )
    for r in results:
        es = r["effect_size"]
        es_str = (
            f"{es:.3f}" if not (isinstance(es, float) and np.isnan(es)) else "N/A"
        )
        print(
            f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
            f"{r['original_effect_size']:>10.3f}  {es_str:>10}  "
            f"{'YES' if r['reproduced'] else 'NO'}"
        )


if __name__ == "__main__":
    main()