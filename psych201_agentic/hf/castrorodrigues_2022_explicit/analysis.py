# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Castro-Rodrigues et al. (2022), "Explicit
knowledge of task structure is a primary determinant of human model-based action",
Nature Human Behaviour, against any dataset in the Psych-301 unified schema.

Effects tested:
- model_free_reward_stay (exp0): In the two-step task, rewards directly reinforce the
  preceding first-stage action — the probability of repeating a first-stage choice
  ('stay') is higher after a rewarded trial than after an unrewarded one. Expected:
  positive reward-dependent stay, significant (model-free reinforcement).
- debrief_increases_model_based (exp0): Explicit task-structure instruction ('debrief')
  increases model-based control — the model-based signature measured as the reward x
  transition interaction on first-stage stay (staying more after a *common*-transition
  reward than after a rare-transition reward) increases after debriefing. Expected:
  positive interaction, larger with debrief.

These are the paper's headline behavioural claims (abstract: "initial behaviour was
model-free, with rewards directly reinforcing preceding actions"; "providing task
structure information strongly increased model-based control"). Model-fit comparisons
are intentionally not included (model performance, not behaviour).
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

EXPERIMENTS = ["exp0", "exp1"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}. loads ./{exp}.csv from CWD unless overridden.

    Required columns per experiment:
      exp0: participant_id, task_id, block, trial, stage, response, reward,
            task_type, debrief, transition_block, valid
      exp1: participant_id, group, ... (same task columns)
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _trial_table(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse the long response-rows into one trial (block) per two-step trial.

    stage1 row holds the first-stage choice (c1); stage2 row holds the second-stage
    choice (c2) and that trial's reward (rw). transition_block is a trial-level label.
    Returns a trial-level table with per-trial choice/reward/transition plus the
    previous trial's choice, reward and transition (for stay / MB analyses).
    """
    df = df[df["valid"] == 1]
    s1 = (
        df[df.stage == "stage1"]
        .set_index(["participant_id", "task_id", "block"])[["response"]]
        .rename(columns={"response": "c1"})
    )
    s2 = (
        df[df.stage == "stage2"]
        .set_index(["participant_id", "task_id", "block"])[["response", "reward"]]
        .rename(columns={"response": "c2", "reward": "rw"})
    )
    st = df.groupby(["participant_id", "task_id", "block"]).first()[
        ["debrief", "task_type", "transition_block"]
    ]
    tr = (
        st.join(s1, on=["participant_id", "task_id", "block"])
        .join(s2, on=["participant_id", "task_id", "block"])
        .reset_index()
        .sort_values(["participant_id", "task_id", "block"])
    )
    tr["prev_c1"] = tr.groupby(["participant_id", "task_id"]).c1.shift(1)
    tr["prev_rw"] = tr.groupby(["participant_id", "task_id"]).rw.shift(1)
    # "orientation" = whether the observed first->second step transition was a
    # matching/crossed pairing (as in the paper's transition coding).
    tr["orient"] = (tr.c1 == tr.c2).astype(int)
    tr["prev_orient"] = tr.groupby(["participant_id", "task_id"]).orient.shift(1)
    tr["prev_tb"] = tr.groupby(["participant_id", "task_id"]).transition_block.shift(1)
    tr["stay"] = (tr.c1 == tr.prev_c1).astype(int)
    # common = the observed transition matches the current transition-structure state.
    tr["common"] = (tr.prev_orient == tr.prev_tb).astype(int)
    return tr


def check_model_free_reward_stay(data: dict[str, pd.DataFrame]) -> dict:
    """\"Initial behaviour was model-free, with rewards directly reinforcing preceding
    actions.\" — Castro-Rodrigues et al. 2022, p.1126, Abstract & Fig. 2.

    Reward-dependent stay on first-stage choices: P(stay | reward) > P(stay | no reward).
    Positive and significant across participants.
    """
    tr = _trial_table(data["exp0"])
    sub = tr.dropna(subset=["stay", "prev_rw", "prev_c1"]).copy()

    stay_diff = (
        sub.groupby("participant_id")
        .apply(
            lambda g: g.stay[g.prev_rw == 1].mean()
            - g.stay[g.prev_rw == 0].mean(),
            include_groups=False,
        )
        .astype(float)
    )
    stay_diff = stay_diff.dropna()
    t, p = stats.ttest_1samp(stay_diff, 0)
    reproduced = bool(t > 0 and p < 0.05)
    return {
        "effect_name": "model_free_reward_stay",
        "experiment": "exp0",
        "original_effect_size": 0.202,  # reward-dependent stay diff (own replication, session 1)
        "effect_size": float(np.mean(stay_diff)),
        "p_value": float(p),
        "n_subjects": int(len(stay_diff)),
        "reproduced": reproduced,
    }


def check_debrief_increases_model_based(data: dict[str, pd.DataFrame]) -> dict:
    """\"Providing task structure information strongly increased model-based control,
    similarly across all groups.\" — Castro-Rodrigues et al. 2022, p.1126, Abstract
    & Fig. 4 / Fig. 5.

    Model-based signature = reward x transition interaction on first-stage stay
    (stay more after a common-transition reward than a rare-transition reward).
    In the debrief group this index increases from the session before (session 3,
    task_id==2) to the session after (session 4, task_id==3) debriefing.
    """
    tr = _trial_table(data["exp0"])
    sub = tr.dropna(subset=["stay", "prev_rw", "common", "prev_c1"]).copy()
    sub = sub[sub.task_type == "fixed"]

    def mb_diff(g):
        rew = g[g.prev_rw == 1]
        com = rew[rew.common == 1].stay.mean()
        rare = rew[rew.common == 0].stay.mean()
        return com - rare

    deb = sub[sub.debrief == "debrief"]
    i3 = deb[deb.task_id == 2].groupby("participant_id").apply(mb_diff)
    i4 = deb[deb.task_id == 3].groupby("participant_id").apply(mb_diff)
    common = sorted(set(i3.index) & set(i4.index))
    i3 = i3[common]
    i4 = i4[common]
    diff = i4 - i3
    t, p = stats.ttest_rel(i4, i3)
    effect_size = float(np.mean(diff))
    reproduced = bool(effect_size > 0 and p < 0.05)
    return {
        "effect_name": "debrief_increases_model_based",
        "experiment": "exp0",
        "original_effect_size": 0.150,  # s3->s4 model-based index increase (own replication)
        "effect_size": effect_size,
        "p_value": float(p),
        "n_subjects": int(len(diff)),
        "reproduced": reproduced,
    }


EFFECTS = [check_model_free_reward_stay, check_debrief_increases_model_based]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. Pure return value."""
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None, help=f"CSV path for {exp}")
    args = ap.parse_args()
    sources = {
        exp: getattr(args, exp)
        for exp in EXPERIMENTS
        if getattr(args, exp)
    }
    for exp in EXPERIMENTS:
        if exp in sources:
            print(f"{exp}: {sources[exp]}")
        else:
            print(f"{exp}: (default — local ./{exp}.csv)")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<4}  {'orig':>8}  {'this':>8}  {'p':>8}  reproduced")
    for r in results:
        print(
            f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
            f"{r['original_effect_size']:>8.3f}  {r['effect_size']:>8.3f}  "
            f"{r['p_value']:>8.3g}  {'YES' if r['reproduced'] else 'NO'}"
        )


if __name__ == "__main__":
    main()