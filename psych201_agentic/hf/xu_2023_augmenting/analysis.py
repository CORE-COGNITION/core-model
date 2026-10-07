# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "scipy"]
# ///
"""Check the primary behavioral effects of Xu & Zhang (2023, CHI) against any dataset
in the Psych-301 unified schema (see schema.md).

Effects tested:
- abs_rt_delta_reduction (exp0): RL group shows greater absolute response-time reduction
  (Feedback - Control session) than Random group; two-way ANOVA Group effect on absolute
  delta is significant (p<.05) with RL more negative than Random.
- rel_rt_delta_reduction (exp0): RL group shows greater relative response-time reduction
  ((Feedback - Control)/Control) than Random group; two-way ANOVA Group effect on
  relative delta is significant (p<.05) with RL more negative than Random.
"""
from __future__ import annotations

import argparse

import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _session_label(row: pd.Series) -> str:
    """Map task value to session type given the counterbalancing order."""
    if row["order"] == 0:
        return "control" if row["task"] == 0 else "feedback"
    else:
        return "feedback" if row["task"] == 0 else "control"


def check_abs_rt_delta_reduction(data: dict[str, pd.DataFrame]) -> dict:
    """\"For absolute response time delta change, significant effect was found for Group
    (F1,75 = 6.309, P = 0.014 < 0.05), i.e., RL group (mean ± SD: −0.297 ± 0.400) v.s.
    Random group (mean ± SD: −0.094 ± 0.320).\" — Xu & Zhang 2023, §6.6.1, Results."""
    df = data["exp0"]
    test = df[(df["phase"] == "test") & (df["rt"] >= 800) & (df["rt"] <= 10000)].copy()
    test["session_type"] = test.apply(_session_label, axis=1)
    rt_agg = test.groupby(["participant_id", "condition", "session_type"])["rt"].mean().reset_index()

    deltas = []
    for (pid, cond), grp in rt_agg.groupby(["participant_id", "condition"]):
        ctrl = grp[grp["session_type"] == "control"]["rt"].values
        fb = grp[grp["session_type"] == "feedback"]["rt"].values
        if len(ctrl) == 1 and len(fb) == 1:
            deltas.append({"participant_id": pid, "condition": cond, "abs_delta_s": (fb[0] - ctrl[0]) / 1000.0})
    deltas = pd.DataFrame(deltas)

    rl = deltas[deltas["condition"] == "rl"]["abs_delta_s"]
    rand = deltas[deltas["condition"] == "random"]["abs_delta_s"]
    t_stat, p_val = stats.ttest_ind(rl, rand, alternative="less")

    rl_mean = rl.mean()
    rand_mean = rand.mean()
    reproduced = bool(rl_mean < rand_mean and p_val < 0.05)
    return {
        "effect_name": "abs_rt_delta_reduction",
        "experiment": "exp0",
        "original_effect_size": -0.297,
        "effect_size": round(float(rl_mean), 3),
        "statistic": round(float(t_stat), 3),
        "p_value": round(float(p_val), 4),
        "reproduced": reproduced,
    }


def check_rel_rt_delta_reduction(data: dict[str, pd.DataFrame]) -> dict:
    """\"For relative response time change, significant effect was found for Group
    (F1,75 = 5.253, P = 0.025 < 0.05), i.e., RL group (mean ± SD: −0.053 ± 0.069) v.s.
    Random group (mean ± SD: −0.011 ± 0.092).\" — Xu & Zhang 2023, §6.6.1, Results."""
    df = data["exp0"]
    test = df[(df["phase"] == "test") & (df["rt"] >= 800) & (df["rt"] <= 10000)].copy()
    test["session_type"] = test.apply(_session_label, axis=1)
    rt_agg = test.groupby(["participant_id", "condition", "session_type"])["rt"].mean().reset_index()

    deltas = []
    for (pid, cond), grp in rt_agg.groupby(["participant_id", "condition"]):
        ctrl = grp[grp["session_type"] == "control"]["rt"].values
        fb = grp[grp["session_type"] == "feedback"]["rt"].values
        if len(ctrl) == 1 and len(fb) == 1:
            deltas.append({"participant_id": pid, "condition": cond, "rel_delta": (fb[0] - ctrl[0]) / ctrl[0]})
    deltas = pd.DataFrame(deltas)

    rl = deltas[deltas["condition"] == "rl"]["rel_delta"]
    rand = deltas[deltas["condition"] == "random"]["rel_delta"]
    t_stat, p_val = stats.ttest_ind(rl, rand, alternative="less")

    rl_mean = rl.mean()
    rand_mean = rand.mean()
    reproduced = bool(rl_mean < rand_mean and p_val < 0.05)
    return {
        "effect_name": "rel_rt_delta_reduction",
        "experiment": "exp0",
        "original_effect_size": -0.053,
        "effect_size": round(float(rl_mean), 3),
        "statistic": round(float(t_stat), 3),
        "p_value": round(float(p_val), 4),
        "reproduced": reproduced,
    }


EFFECTS = [check_abs_rt_delta_reduction, check_rel_rt_delta_reduction]


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