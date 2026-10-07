# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Kool, Cushman, & Gershman (2016),
"When does model-based control pay off?" (PLoS Comput Biol 12(8): e1005090),
against any dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- daw_stay_reward_maineffect (exp0): in the standard Daw two-step task, reward on
  the previous trial increases the probability of staying with the previous
  first-stage choice (main effect of reward on stay; fig 16A). One-sample t-test
  of the per-participant win-minus-loss stay contrast, expected > 0 for
  reproduction of the model-free signature.
- daw_stay_reward_common_interaction (exp0): staying is higher after reward on
  common transitions and after no-reward on rare transitions (the model-based
  crossover interaction between previous reward and transition type; fig 16A).
  One-sample t-test of the per-participant interaction contrast, expected > 0.
- novel_stay_same_vs_diff_after_reward (exp1): in the novel two-step task, a
  positive reward on the previous trial enhances staying behavior from chance in
  both the same and the different start-state conditions, and this effect is
  larger when the current first-stage state equals the previous trial's state
  (fig 16B). Paired t-test same > different, plus one-sample tests vs chance
  (0.5) for both conditions, all expected p < .05.

NOTE: The paper's remaining headline claims rest on the model-based weighting
parameter w per participant estimated from hybrid RL model fits (median w: 0.27
Daw vs 0.48 novel; Wilcoxon z = 3.31, p < .001; and w vs reward-rate r = 0.55,
p < .001 for the novel task only). w is not recoverable from raw trial choice
data alone, so we check the paper's single-trial behavioral signatures (the
stay-probability analyses of Fig 16, computed exactly as in the authors'
groupanalysis.m) instead — the interaction between previous reward and (a)
transition type in the Daw task and (b) start-state similarity in the novel
task is the standard conceptually-equivalent behavioral fingerprint of
model-based over model-free control.
"""
from __future__ import annotations

import argparse
from statistics import mean

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0", "exp1"]

# exclusion criterion identical to the authors' groupanalysis.m:
# drop participants with >= 25 missed (timed-out) trials in the test phase
MAX_MISSED = 25


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD — `cd` into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      exp0: participant_id, trial, block, phase, stage, response, reward,
            common, valid, stim_1_left, stim_1_right
      exp1: participant_id, trial, block, phase, response, reward, state,
            state1, state2, valid
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _keep_participants(df: pd.DataFrame) -> pd.DataFrame:
    """Drop participants with >= MAX_MISSED timed-out (valid==0) test trials."""
    test = df[df["phase"] == "test"]
    if "stage" in df.columns:
        per_trial = test.groupby(["participant_id", "block"])["valid"].min().reset_index()
        n_missed = per_trial.groupby("participant_id")["valid"].apply(lambda v: (v == 0).sum())
    else:
        n_missed = test.groupby("participant_id")["valid"].apply(lambda v: (v == 0).sum())
    keep = set(n_missed[n_missed < MAX_MISSED].index)
    return df[df["participant_id"].isin(keep)]


def check_daw_stay_reward_maineffect(data: dict[str, pd.DataFrame]) -> dict:
    """"For the participants who completed the Daw task, we found that a reward
    on the previous trial increased the probability of staying with the previous
    trial's choice [t(196) = 7.70, p < 0.001; Fig 16A]" — Kool et al. 2016,
    p.24, Results / Behavioral performance."""
    df = _keep_participants(data["exp0"])
    s1 = df[(df["phase"] == "test") & (df["stage"] == "stage1") & (df["valid"] == 1)]
    s2 = df[(df["phase"] == "test") & (df["stage"] == "stage2")][
        ["participant_id", "block", "reward", "valid"]].rename(
        columns={"reward": "prev_reward", "valid": "prev_valid"})
    m = s1[["participant_id", "block", "response"]].merge(s2, on=["participant_id", "block"])
    m = m.sort_values(["participant_id", "block"])
    for pid, sub in m.groupby("participant_id", sort=False):
        m.loc[sub.index, "stay"] = (sub["response"] == sub["response"].shift(1)).astype(float)
        m.loc[sub.index, "prev_rew"] = sub["prev_reward"].shift(1)
        m.loc[sub.index, "prev_valid"] = sub["prev_valid"].shift(1)
    m = m[m["prev_rew"].notna() & (m["prev_valid"] == 1)]
    cell = m.groupby("participant_id").apply(
        lambda g: pd.Series({
            "win": g.loc[g["prev_rew"] > 0, "stay"].mean(),
            "loss": g.loc[g["prev_rew"] <= 0, "stay"].mean(),
        }), include_groups=False).dropna()
    contrast = cell["win"] - cell["loss"]
    t, p = stats.ttest_1samp(contrast, 0)
    reproduced = bool(t > 0 and p < 0.05)
    return {
        "effect_name": "daw_stay_reward_maineffect",
        "experiment": "exp0",
        "original_effect_size": 7.70 / np.sqrt(197.0),   # d = t/sqrt(n), t(196)=7.70
        "effect_size": float(contrast.mean()),
        "t": float(t), "p": float(p), "n": int(contrast.notna().sum()),
        "reproduced": reproduced,
    }


def check_daw_stay_reward_common_interaction(data: dict[str, pd.DataFrame]) -> dict:
    """...but that this effect interacted with the type of transition on the
    previous trial [t(196) = 5.38, p < 0.001]." — Kool et al. 2016, p.24, Results /
    Behavioral performance (the model-based crossover; fig 16A)."""
    df = _keep_participants(data["exp0"])
    s1 = df[(df["phase"] == "test") & (df["stage"] == "stage1") & (df["valid"] == 1)]
    s2 = df[(df["phase"] == "test") & (df["stage"] == "stage2")][
        ["participant_id", "block", "reward", "common", "valid"]].rename(
        columns={"reward": "prev_reward", "common": "prev_common", "valid": "prev_valid"})
    m = s1[["participant_id", "block", "response"]].merge(s2, on=["participant_id", "block"])
    m = m.sort_values(["participant_id", "block"])
    for pid, sub in m.groupby("participant_id", sort=False):
        m.loc[sub.index, "stay"] = (sub["response"] == sub["response"].shift(1)).astype(float)
        m.loc[sub.index, "prev_rew"] = sub["prev_reward"].shift(1)
        m.loc[sub.index, "prev_common"] = sub["prev_common"].shift(1)
        m.loc[sub.index, "prev_valid"] = sub["prev_valid"].shift(1)
    m = m[m["prev_rew"].notna() & m["prev_common"].notna() & (m["prev_valid"] == 1)]
    cell = m.groupby("participant_id").apply(
        lambda g: pd.Series({
            "win_common": g.loc[(g["prev_rew"] > 0) & (g["prev_common"] == 1), "stay"].mean(),
            "win_rare": g.loc[(g["prev_rew"] > 0) & (g["prev_common"] == 0), "stay"].mean(),
            "loss_common": g.loc[(g["prev_rew"] <= 0) & (g["prev_common"] == 1), "stay"].mean(),
            "loss_rare": g.loc[(g["prev_rew"] <= 0) & (g["prev_common"] == 0), "stay"].mean(),
        }), include_groups=False)
    interaction = (cell["win_common"] + cell["loss_rare"]) - (cell["win_rare"] + cell["loss_common"])
    t, p = stats.ttest_1samp(interaction.dropna(), 0)
    reproduced = bool(t > 0 and p < 0.05)
    return {
        "effect_name": "daw_stay_reward_common_interaction",
        "experiment": "exp0",
        "original_effect_size": 5.38 / np.sqrt(197.0),   # d = t/sqrt(n), t(196)=5.38
        "effect_size": float(interaction.mean()),
        "t": float(t), "p": float(p), "n": int(interaction.notna().sum()),
        "reproduced": reproduced,
    }


def check_novel_stay_same_vs_diff_after_reward(data: dict[str, pd.DataFrame]) -> dict:
    """"For the participants who completed the new paradigm, we found that a
    positive reward on the previous trial significantly enhanced staying behavior
    from chance for both similar and different current start states, (p < 0.001
    for both effects), but this effect was larger for the same compared to the
    different start state condition [t(183) = 9.64, p < 0.001; Fig 16B]" — Kool
    et al. 2016, p.24, Results / Behavioral performance."""
    df = _keep_participants(data["exp1"])
    test = df[(df["phase"] == "test") & (df["valid"] == 1)].sort_values(
        ["participant_id", "block"])
    for pid, sub in test.groupby("participant_id", sort=False):
        test.loc[sub.index, "stay"] = (
            sub["state2"] == sub["state2"].shift(1)).astype(float)
        test.loc[sub.index, "same"] = (
            sub["state1"] == sub["state1"].shift(1)).astype(float)
        test.loc[sub.index, "prev_rew"] = sub["reward"].shift(1)
    test = test[test["prev_rew"].notna()]
    won = test[test["prev_rew"] > 0]
    cell = won.groupby("participant_id").apply(
        lambda g: pd.Series({
            "same": g.loc[g["same"] == 1, "stay"].mean(),
            "diff": g.loc[g["same"] == 0, "stay"].mean(),
        }), include_groups=False).dropna()
    t_same, p_same = stats.ttest_1samp(cell["same"], 0.5)
    t_diff, p_diff = stats.ttest_1samp(cell["diff"], 0.5)
    t_paired, p_paired = stats.ttest_rel(cell["same"], cell["diff"])
    reproduced = bool(
        cell["same"].mean() > cell["diff"].mean()
        and p_paired < 0.05 and p_same < 0.05 and p_diff < 0.05)
    return {
        "effect_name": "novel_stay_same_vs_diff_after_reward",
        "experiment": "exp1",
        "original_effect_size": 9.64 / np.sqrt(184.0),   # d = t/sqrt(n), t(183)=9.64
        "effect_size": float((cell["same"] - cell["diff"]).mean()),
        "stay_same": float(cell["same"].mean()),
        "stay_diff": float(cell["diff"].mean()),
        "t_paired": float(t_paired), "p_paired": float(p_paired),
        "p_same_chance": float(p_same), "p_diff_chance": float(p_diff),
        "n": int(len(cell)),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_daw_stay_reward_maineffect,
    check_daw_stay_reward_common_interaction,
    check_novel_stay_same_vs_diff_after_reward,
]


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
        extra = ""
        if "p" in r:
            extra = f"  (t={r['t']:.2f}, p={r['p']:.3g}, n={r['n']})"
        if "p_paired" in r:
            extra = (f"  (t={r['t_paired']:.2f}, p={r['p_paired']:.3g}, "
                     f"stay_same={r['stay_same']:.3f}, stay_diff={r['stay_diff']:.3f}, n={r['n']})")
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}{extra}")


if __name__ == "__main__":
    main()