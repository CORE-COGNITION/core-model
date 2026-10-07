# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Russek et al. 2024 (Nature Communications
15:4269) against any dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- additive_heuristic_components_drive_choice (exp0): logistic regression of
  accept/reject on the additive-heuristic probability component (P_better - P_worse)
  and reward component (mean(o1,o2) - safe). Both coefficients expected positive and
  significant; this is the aggregate pattern in Fig. 2B.
- rt_prob_prioritization_relates_to_choice_prob_weight (exp1): per-participant
  response-time probability weight (effect of probed-stimulus probability on log RT)
  negatively related (spearman) to choice probability weight. Paper: r=-.183, p=.044.
- rt_reward_prioritization_relates_to_choice_reward_weight (exp1): per-participant
  response-time reward weight (effect of probed-stimulus absolute reward on log RT)
  negatively related (spearman) to choice reward weight. Paper: r=-.21, p=.025.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import statsmodels.formula.api as smf

EXPERIMENTS = ["exp0", "exp1"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD -- `cd` into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      exp0: participant_id, response, accept, p_o1, o1_val, o2_val, safe_val, rt
      exp1: participant_id, response, accept, p_o1, o1_val, o2_val, safe_val, rt,
            recognition_number, condition, valid, o1_image, o2_image, safe_image
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _additive_components(df: pd.DataFrame) -> pd.DataFrame:
    """Build the additive-heuristic regressors for choice data.

    win_prob = P(better outcome) - P(worse outcome), where "better" is the gamble
    outcome with the higher point value (Eq. 2 / evaluate_add in the analysis code).
    rew_comp = The reward component, mean(O1,O2) - safe (Eq. 2).
    """
    out = df.copy()
    better = out["o1_val"] > out["o2_val"]
    out["win_prob"] = np.where(better, 2 * out["p_o1"] - 1, 1 - 2 * out["p_o1"])
    out["rew_comp"] = (out["o1_val"] + out["o2_val"]) / 2 - out["safe_val"]
    return out


def _exclude_consistent(df: pd.DataFrame) -> pd.DataFrame:
    """Drop participants who accepted the same action >80% or <20% of the time
    (the paper's exclusion; Russek et al. 2024, Methods)."""
    frac = df.groupby("participant_id")["accept"].mean()
    bad = frac[(frac > 0.8) | (frac < 0.2)].index
    return df[~df["participant_id"].isin(bad)].copy()


def _choice_weights(df: pd.DataFrame) -> dict[str, tuple[float, float]]:
    """Per-participant additive-heuristic choice weights (beta_prob, beta_reward)."""
    weights = {}
    df = _additive_components(df)
    df = df[df["accept"].notna()]
    df = _exclude_consistent(df)
    for s, sd in df.groupby("participant_id"):
        inter = " + C(gl_type)" if "gl_type" in sd.columns else ""
        try:
            m = smf.logit(f"accept ~ win_prob + rew_comp{inter}", sd).fit(
                disp=0, maxiter=300
            )
            weights[s] = (float(m.params["win_prob"]), float(m.params["rew_comp"]))
        except Exception:
            try:
                m = smf.logit("accept ~ win_prob + rew_comp", sd).fit(
                    disp=0, maxiter=300
                )
                weights[s] = (float(m.params["win_prob"]), float(m.params["rew_comp"]))
            except Exception:
                continue
    return weights


def _rt_weights(df: pd.DataFrame, subs: set) -> dict[str, tuple[float, float]]:
    """Per-participant response-time weights (beta_prob(RT), beta_reward(RT)) from
    Eq. 8: log rt ~ probe_prob + probe_reward + probed_image, on detection trials
    where a gamble outcome was probed (recognition_number 1/2 = O1/O2)."""
    recog = df["recognition_number"] if "recognition_number" in df else None
    if recog is None:
        return {}
    det = df[(recog > 0) & df["rt"].notna()].copy()
    if "valid" in det.columns:
        det = det[det["valid"] == 1]
    det = det[det["participant_id"].isin(subs)]
    if det.empty:
        return {}
    det["p_o2"] = 1 - det["p_o1"]
    det["probe_prob"] = det["p_o1"] - 0.5
    det.loc[det["recognition_number"] == 2, "probe_prob"] = det["p_o2"] - 0.5
    det.loc[det["recognition_number"] == 3, "probe_prob"] = 0.0
    det["probe_rew"] = det["o1_val"].abs() - det["o2_val"].abs()
    det.loc[det["recognition_number"] == 2, "probe_rew"] = (
        -det["o1_val"].abs() + det["o2_val"].abs()
    )
    det.loc[det["recognition_number"] == 3, "probe_rew"] = 0.0
    det["log_rt"] = np.log(det["rt"])
    weights = {}
    for s, sd0 in det.groupby("participant_id"):
        sd = sd0
        if all(c in sd.columns for c in ("o1_image", "o2_image", "safe_image")):
            sd = sd.copy()
            sd["probed_image"] = sd["o1_image"]
            sd.loc[sd["recognition_number"] == 2, "probed_image"] = sd["o2_image"]
            sd.loc[sd["recognition_number"] == 3, "probed_image"] = sd["safe_image"]
            formula = "log_rt ~ probe_prob + probe_rew + C(probed_image)"
        else:
            formula = "log_rt ~ probe_prob + probe_rew"
        try:
            m = smf.ols(formula, sd).fit()
            weights[s] = (float(m.params["probe_prob"]), float(m.params["probe_rew"]))
        except Exception:
            continue
    return weights


def check_additive_heuristic_components_drive_choice(data: dict[str, pd.DataFrame]) -> dict:
    """"The additive heuristic model captured participants' aggregate choices ...
    It captured both deviations from a model that decided by computing expected values
    (Fig. 2B) and the extent to which individual participants relied on either
    probability or reward information in choice (Fig. 2C)." - Russek et al. 2024, p.2,
    Results.
    """
    df = _additive_components(data["exp0"])
    df = df[df["accept"].notna()]
    df = _exclude_consistent(df)
    inter = " + C(gl_type)" if "gl_type" in df.columns else ""
    m = smf.logit(f"accept ~ win_prob + rew_comp{inter}", df).fit(disp=0, maxiter=300)
    b_prob, p_prob = float(m.params["win_prob"]), float(m.pvalues["win_prob"])
    b_rew, p_rew = float(m.params["rew_comp"]), float(m.pvalues["rew_comp"])
    reproduced = bool(b_prob > 0 and p_prob < 0.05 and b_rew > 0 and p_rew < 0.05)
    return {
        "effect_name": "additive_heuristic_components_drive_choice",
        "experiment": "exp0",
        "original_effect_size": 1.0,
        "effect_size": float(b_prob),
        "reproduced": reproduced,
        "prob_coef": b_prob,
        "prob_p": p_prob,
        "rew_coef": b_rew,
        "rew_p": p_rew,
    }


def check_rt_prob_prioritization_relates_to_choice_prob_weight(
    data: dict[str, pd.DataFrame],
) -> dict:
    """"a greater tendency to use probability information in choice ... related to a
    greater tendency to represent outcomes based on their probability (measured as
    lower beta_prob(RT)...; spearman rank correlation, one-tailed;
    r_spearman = -.183, t(86) = -1.72, P = .044; Fig. 6B)." - Russek et al. 2024,
    p.8, Results (Perceptual detection task).
    """
    cw = _choice_weights(data["exp1"])
    rw = _rt_weights(data["exp1"], set(cw))
    subs = sorted(set(cw) & set(rw))
    cp = np.array([cw[s][0] for s in subs])
    rp = np.array([rw[s][0] for s in subs])
    if len(subs) < 10:
        return {
            "effect_name": "rt_prob_prioritization_relates_to_choice_prob_weight",
            "experiment": "exp1",
            "original_effect_size": -0.183,
            "effect_size": float("nan"),
            "reproduced": False,
            "n": len(subs),
        }
    r, p_two = spearmanr(cp, rp)
    p_one = p_two / 2
    reproduced = bool(r < 0 and p_one < 0.05)
    return {
        "effect_name": "rt_prob_prioritization_relates_to_choice_prob_weight",
        "experiment": "exp1",
        "original_effect_size": -0.183,
        "effect_size": float(r),
        "reproduced": reproduced,
        "p_onesided": float(p_one),
        "n": len(subs),
    }


def check_rt_reward_prioritization_relates_to_choice_reward_weight(
    data: dict[str, pd.DataFrame],
) -> dict:
    """"a greater tendency to use reward information in choice ... related to a greater
    tendency to represent outcomes based on their reward (measured as lower
    beta_reward(RT)...; spearman rank correlation, one-tailed, r_spearman = -.21,
    t(86) = -2.0, P = .025; Fig. 6C)." - Russek et al. 2024, p.8, Results
    (Perceptual detection task).
    """
    cw = _choice_weights(data["exp1"])
    rw = _rt_weights(data["exp1"], set(cw))
    subs = sorted(set(cw) & set(rw))
    cr = np.array([cw[s][1] for s in subs])
    rr = np.array([rw[s][1] for s in subs])
    if len(subs) < 10:
        return {
            "effect_name": "rt_reward_prioritization_relates_to_choice_reward_weight",
            "experiment": "exp1",
            "original_effect_size": -0.21,
            "effect_size": float("nan"),
            "reproduced": False,
            "n": len(subs),
        }
    r, p_two = spearmanr(cr, rr)
    p_one = p_two / 2
    reproduced = bool(r < 0 and p_one < 0.05)
    return {
        "effect_name": "rt_reward_prioritization_relates_to_choice_reward_weight",
        "experiment": "exp1",
        "original_effect_size": -0.21,
        "effect_size": float(r),
        "reproduced": reproduced,
        "p_onesided": float(p_one),
        "n": len(subs),
    }


EFFECTS = [
    check_additive_heuristic_components_drive_choice,
    check_rt_prob_prioritization_relates_to_choice_prob_weight,
    check_rt_reward_prioritization_relates_to_choice_reward_weight,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. No printing -- pure return value
    so downstream simulators / model evaluators can call this programmatically."""
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(
            f"--{exp}", default=None, help=f"CSV path for {exp}; defaults to ./{exp}.csv in CWD"
        )
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS if getattr(args, exp)}
    for exp in EXPERIMENTS:
        if exp in sources:
            print(f"{exp}: {sources[exp]}")
        else:
            print(f"{exp}: (default -- local ./{exp}.csv)")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  reproduced")
    for r in results:
        print(
            f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
            f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
            f"{'YES' if r['reproduced'] else 'NO'}"
        )


if __name__ == "__main__":
    main()