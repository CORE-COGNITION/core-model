# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Witte, Thalmann & Schulz (2024) "How
should we measure exploration?" against any dataset in the Psych-301 unified schema.

Effects tested:
- switch_prob_retest (all bandit tasks): Test-retest reliability of switch
  probability between session1 and session2. Expected: significant positive
  Pearson r for each task (p < .05).
- switch_prob_convergent (all bandit tasks): Cross-task correlations of switch
  probability within a session. Expected: all pairwise Pearson r positive and
  significant (p < .05), consistent with reported range 0.36-0.49.
- horizon_value_guided (exp0, task_id=0): On the first free choice of each
  Horizon block, participants choose the arm with higher expected value.
  Expected: logistic regression coefficient for value_diff > 0, p < .05.
- horizon_directed (exp0, task_id=0): Participants weight uncertainty more
  heavily in the long-horizon condition. Expected: logistic regression
  coefficient for unc_diff * horizon interaction > 0, p < .05.
"""
from __future__ import annotations

import argparse
import warnings

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

warnings.filterwarnings("ignore", category=FutureWarning)

EXPERIMENTS = ["exp0"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv"), low_memory=False)
            for exp in EXPERIMENTS}


def check_switch_prob_retest(data: dict[str, pd.DataFrame]) -> dict:
    """\"the task-based measures, including performance and switch probability,
    exhibited moderate to good reliability\" — Witte et al. 2024, p.3, Results
    (Reliability)."""
    df = data["exp0"]
    bandit = df[(df["task_id"].isin([0, 1, 2])) & (df["valid"] == 1)].copy()
    bandit = bandit.sort_values(["participant_id", "session", "task_id", "trial"])

    def _switch_prob(grp):
        resp = grp["response"].values
        if len(resp) < 2:
            return np.nan
        return float((resp[1:] != resp[:-1]).mean())

    sp = bandit.groupby(["participant_id", "session", "task_id"]).apply(
        _switch_prob, include_groups=False
    ).reset_index()
    sp.columns = ["participant_id", "session", "task_id", "p_switch"]

    task_map = {0: "Horizon", 1: "TwoArmed", 2: "Restless"}
    reproduced_all = True
    rs = []
    for tid in [0, 1, 2]:
        s1 = sp[(sp["task_id"] == tid) & (sp["session"] == "session1")].set_index("participant_id")["p_switch"]
        s2 = sp[(sp["task_id"] == tid) & (sp["session"] == "session2")].set_index("participant_id")["p_switch"]
        common = s1.index.intersection(s2.index)
        if len(common) < 5:
            reproduced_all = False
            r_val = 0.0
            p_val = 1.0
        else:
            r_val, p_val = stats.pearsonr(s1[common], s2[common])
        rep = r_val > 0 and p_val < 0.05
        if not rep:
            reproduced_all = False
        rs.append({"task": task_map[tid], "r": r_val, "p": p_val, "reproduced": rep})

    return {
        "effect_name": "switch_prob_retest",
        "experiment": "exp0",
        "original_effect_size": 0.6,
        "effect_size": np.mean([r["r"] for r in rs]),
        "reproduced": reproduced_all,
        "details": rs,
    }


def check_switch_prob_convergent(data: dict[str, pd.DataFrame]) -> dict:
    """\"this measure of exploration seemed reasonably consistent across tasks
    with correlations between 0.36 and 0.49\" — Witte et al. 2024, p.5, Results
    (Convergent Validity)."""
    df = data["exp0"]
    bandit = df[(df["task_id"].isin([0, 1, 2])) & (df["valid"] == 1)].copy()
    bandit = bandit.sort_values(["participant_id", "session", "task_id", "trial"])

    def _switch_prob(grp):
        resp = grp["response"].values
        if len(resp) < 2:
            return np.nan
        return float((resp[1:] != resp[:-1]).mean())

    sp = bandit.groupby(["participant_id", "session", "task_id"]).apply(
        _switch_prob, include_groups=False
    ).reset_index()
    sp.columns = ["participant_id", "session", "task_id", "p_switch"]

    pairs = [(0, 1), (0, 2), (1, 2)]
    task_map = {0: "Horizon", 1: "TwoArmed", 2: "Restless"}
    reproduced_all = True
    rs = []
    for session_label in ["session1", "session2"]:
        s_sp = sp[sp["session"] == session_label].pivot_table(
            index="participant_id", columns="task_id", values="p_switch"
        )
        for t1, t2 in pairs:
            pair = s_sp[[t1, t2]].dropna()
            if len(pair) < 5:
                reproduced_all = False
                r_val = 0.0
                p_val = 1.0
            else:
                r_val, p_val = stats.pearsonr(pair[t1], pair[t2])
            rep = r_val > 0 and p_val < 0.05
            if not rep:
                reproduced_all = False
            rs.append({
                "session": session_label,
                "pair": f"{task_map[t1]}-{task_map[t2]}",
                "r": r_val, "p": p_val, "reproduced": rep,
            })

    return {
        "effect_name": "switch_prob_convergent",
        "experiment": "exp0",
        "original_effect_size": 0.42,
        "effect_size": np.mean([r["r"] for r in rs]),
        "reproduced": reproduced_all,
        "details": rs,
    }


def _horizon_first_free(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    df = data["exp0"]
    h = df[(df["task_id"] == 0) & (df["valid"] == 1)].copy()
    forced = h[h["forced_choice"] == 1]
    arm_counts = forced.groupby(
        ["participant_id", "session", "block", "response"]
    ).size().unstack(fill_value=0)
    arm_counts.columns = ["arm0_count", "arm1_count"]
    arm_counts = arm_counts.reset_index()

    ff = h[h["forced_choice"] == 0].groupby(
        ["participant_id", "session", "block"]
    ).first().reset_index()
    ff = ff.merge(arm_counts, on=["participant_id", "session", "block"])

    forced_means = forced.groupby(
        ["participant_id", "session", "block", "response"]
    )["reward"].mean().reset_index()
    for arm in [0, 1]:
        sub = forced_means[forced_means["response"] == arm][
            ["participant_id", "session", "block", "reward"]
        ]
        sub.columns = ["participant_id", "session", "block", f"e_arm{arm}"]
        ff = ff.merge(sub, on=["participant_id", "session", "block"], how="left")

    ff["value_diff"] = ff["e_arm1"] - ff["e_arm0"]
    ff["unc_arm1"] = 1.0 / np.sqrt(ff["arm1_count"].clip(lower=1))
    ff["unc_arm0"] = 1.0 / np.sqrt(ff["arm0_count"].clip(lower=1))
    ff["unc_diff"] = ff["unc_arm1"] - ff["unc_arm0"]
    ff["horizon_c"] = ff["horizon"] - 7.5
    ff["vd_h"] = ff["value_diff"] * ff["horizon_c"]
    ff["ud_h"] = ff["unc_diff"] * ff["horizon_c"]
    return ff


def check_horizon_value_guided(data: dict[str, pd.DataFrame]) -> dict:
    """\"people explore more in the long horizon condition than in the short
    horizon condition\" — Witte et al. 2024, p.6, Improving the Measurement.
    Value-guided: participants choose higher-value arms on first free choice."""
    ff = _horizon_first_free(data)
    valid = ff[["value_diff", "response"]].dropna()
    if len(valid) < 50:
        return {"effect_name": "horizon_value_guided", "experiment": "exp0",
                "original_effect_size": 0.12, "effect_size": 0.0,
                "reproduced": False}
    
    X = sm.add_constant(valid[["value_diff"]].fillna(0))
    model = sm.Logit(valid["response"], X)
    result = model.fit(disp=False, maxiter=200)
    coef = result.params["value_diff"]
    p_val = result.pvalues["value_diff"]
    reproduced = coef > 0 and p_val < 0.05
    return {
        "effect_name": "horizon_value_guided",
        "experiment": "exp0",
        "original_effect_size": 0.12,
        "effect_size": float(coef),
        "reproduced": reproduced,
    }


def check_horizon_directed(data: dict[str, pd.DataFrame]) -> dict:
    """\"the increase in directed exploration from the short to the long horizon
    condition\" — Witte et al. 2024, p.6, Improving the Measurement. Directed
    exploration: uncertainty-weighting increases in the long horizon."""
    ff = _horizon_first_free(data)
    ff["horizon_c"] = ff["horizon"] - 7.5
    ff["ud_h"] = ff["unc_diff"] * ff["horizon_c"]
    valid = ff[["value_diff", "unc_diff", "horizon_c", "ud_h", "response"]].dropna()
    if len(valid) < 50:
        return {"effect_name": "horizon_directed", "experiment": "exp0",
                "original_effect_size": 0.11, "effect_size": 0.0,
                "reproduced": False}

    X = sm.add_constant(valid[["value_diff", "unc_diff", "horizon_c", "ud_h"]].fillna(0))
    model = sm.Logit(valid["response"], X)
    result = model.fit(disp=False, maxiter=200)
    coef = result.params["ud_h"]
    p_val = result.pvalues["ud_h"]
    reproduced = coef > 0 and p_val < 0.05
    return {
        "effect_name": "horizon_directed",
        "experiment": "exp0",
        "original_effect_size": 0.11,
        "effect_size": float(coef),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_switch_prob_retest,
    check_switch_prob_convergent,
    check_horizon_value_guided,
    check_horizon_directed,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None,
                        help=f"CSV path for {exp}; defaults to ./{exp}.csv in CWD")
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS
               if getattr(args, exp)}
    for exp in EXPERIMENTS:
        if exp in sources:
            print(f"{exp}: {sources[exp]}")
        else:
            print(f"{exp}: (default — local ./{exp}.csv)")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    header = f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  reproduced"
    print(header)
    print("-" * len(header))
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")
        if "details" in r:
            for d in r["details"]:
                extra = {k: v for k, v in d.items() if k != "reproduced"}
                rep_str = "YES" if d.get("reproduced") else "NO"
                print(f"  {'':<{w}}  {'':<4}  {str(extra):>30}  {rep_str}")


if __name__ == "__main__":
    main()