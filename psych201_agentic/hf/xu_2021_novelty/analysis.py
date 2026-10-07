# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Xu, Modirshanechi, Lehmann, Gerstner &
Herzog (2021, PLoS Comput Biol) "Novelty is not surprise: Human exploratory and
adaptive behavior in sequential decision-making" against any dataset in the
Psych-301 unified schema (see schema.md).

This experiment is a single sequential grid-world task (the "SwitchState" task).
Each participant runs 5 episodes in block 1 (env 3; novel environment — novelty /
exploration phase) and 5 episodes in block 2 (env 4; a swap of the transitions of
two states tests surprise-driven re-adaptation). Every trial is one discrete action
(a move) with reward feedback given only when the goal is reached.

The environment is deterministic, so the transition structure is recovered from
the data itself: for each block the modal next_state for each (state, action) pair
defines the transition function, shortest-path distances to the goal (state 10) are
computed by BFS, and each action is classified as good (strictly decreases distance
to goal), neutral (self-loop), or bad (increases distance). Progressing states are
those with exactly one good, one neutral and two bad actions (the 7 path states of
the task); the swapped states in block 2 are the progressing states whose good
action changes between the two blocks.

Effects tested:
- novelty_driven_exploration (exp0): in the 1st episode of block 1, before any
  reward is found, participants at progressing states choose according to progress
  significantly above the random-exploration baseline of zero (good=1, neutral=0.5,
  bad=-0.75). One-sample t-test across participants of mean per-participant progress.
- surprise_driven_readaptation (exp0): after the state swap, in the 1st episode of
  block 2, participants at the swapped states choose the (post-swap) good action
  significantly more often than chance (0.25). One-sample t-test across participants.
- reward_learning_over_episodes (exp0): participants learn the path over episodes;
  the number of actions taken to reach the goal in episode 1 of block 1 is
  significantly larger than the mean number taken in episodes 2-5 (paired t-test).
"""
from __future__ import annotations

import argparse
import collections
from typing import Optional

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0"]

GOOD, NEUTRAL, BAD = 1.0, 0.5, -0.75
GOAL_STATE = 10


def load_data(sources: Optional[dict[str, str]] = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD — `cd` into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      exp0: participant_id, block, epi, state, response, next_state
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _transitions(df: pd.DataFrame, block: int) -> dict[tuple[int, int], int]:
    """Modal next_state for each (state, action) pair in a block (deterministic env)."""
    sub = df[df["block"] == block]
    t: dict[tuple[int, int], int] = {}
    for (s, a), g in sub.groupby(["state", "response"]):
        t[(s, a)] = int(g["next_state"].mode().iloc[0])
    return t


def _bfs_distances(t: dict[tuple[int, int], int]) -> dict[int, int]:
    """Shortest-path distance from each state to the goal (GOAL_STATE)."""
    rev: dict[int, set[int]] = collections.defaultdict(set)
    for (s, a), ns in t.items():
        rev[ns].add(s)
    dist = {GOAL_STATE: 0}
    queue = collections.deque([GOAL_STATE])
    while queue:
        ns = queue.popleft()
        for s in rev.get(ns, ()):
            if s not in dist:
                dist[s] = dist[ns] + 1
                queue.append(s)
    return dist


def _classify_actions(t: dict[tuple[int, int], int], dist: dict[int, int], s: int) -> dict[int, str]:
    cls: dict[int, str] = {}
    for a in range(4):
        nd = dist.get(t.get((s, a)))
        if nd is None:
            cls[a] = "bad"
        elif nd < dist[s]:
            cls[a] = "good"
        elif nd == dist[s]:
            cls[a] = "neutral"
        else:
            cls[a] = "bad"
    return cls


def _env_structure(df: pd.DataFrame, block: int) -> tuple[dict[int, dict[int, str]], set[int]]:
    """Per-state action classification and the set of progressing states for a block."""
    t = _transitions(df, block)
    dist = _bfs_distances(t)
    cls = {s: _classify_actions(t, dist, s) for s in dist if s != GOAL_STATE}
    progressing = {
        s
        for s in cls
        if sum(v == "good" for v in cls[s].values()) == 1
        and sum(v == "neutral" for v in cls[s].values()) == 1
        and sum(v == "bad" for v in cls[s].values()) == 2
    }
    return cls, progressing


def check_novelty_driven_exploration(data: dict[str, pd.DataFrame]) -> dict:
    """"With increasing experience, the latency of escape from the trap states was reduced
    (Fig2A) and the good actions at progressing states were chosen with higher probability
    (Fig2B). ... to note that these improvements were observed in the absence of any external
    feedback indicating progress and before the 1st encounter of the goal state." — Xu et al.
    2021, Results, p.3. Random-baseline progress is zero ("average progress vanishes for random
    exploration", Fig 2 caption): the check is per-participant mean progress (good=1,
    neutral=0.5, bad=-0.75) at progressing states in episode 1 of block 1 > 0."""
    df = data["exp0"]
    cls, progressing = _env_structure(df, 0)
    sub = df[(df["block"] == 0) & (df["epi"] == 1) & (df["state"].isin(progressing))]
    progress = []
    for _, g in sub.groupby("participant_id"):
        vals = [GOOD if cls[r["state"]][r["response"]] == "good"
                else NEUTRAL if cls[r["state"]][r["response"]] == "neutral"
                else BAD for _, r in g.iterrows()]
        progress.append(np.mean(vals))
    progress = np.array(progress)
    t_stat, p = stats.ttest_1samp(progress, 0)
    reproduced = bool(p < 0.05 and np.mean(progress) > 0)
    return {
        "effect_name": "novelty_driven_exploration",
        "experiment": "exp0",
        "original_effect_size": 0.0,
        "effect_size": float(np.mean(progress)),
        "p": float(p),
        "t": float(t_stat),
        "reproduced": reproduced,
    }


def check_surprise_driven_readaptation(data: dict[str, pd.DataFrame]) -> dict:
    """"After the swap, participants continued escaping from the trap states ... and choosing
    the good actions at the unchanged progressing states ... Moreover, they rapidly adapted
    their behavior and found the new good actions at the swapped states (state 7 in Fig 2C)."
    — Xu et al. 2021, Results, p.3. The check: in the 1st episode of block 2 at the swapped
    progressing states (those whose good action changed between block 1 and block 2),
    participants choose the post-swap good action significantly more often than chance (0.25)."""
    df = data["exp0"]
    cls0, prog0 = _env_structure(df, 0)
    cls1, prog1 = _env_structure(df, 1)
    swapped = [s for s in prog0 & prog1 if cls0[s] != cls1[s]]
    sub = df[(df["block"] == 1) & (df["epi"] == 1) & (df["state"].isin(swapped))]
    rates = []
    for _, g in sub.groupby("participant_id"):
        rate = np.mean([1 if cls1[r["state"]][r["response"]] == "good" else 0 for _, r in g.iterrows()])
        rates.append(rate)
    rates = np.array(rates)
    t_stat, p = stats.ttest_1samp(rates, 0.25)
    reproduced = bool(p < 0.05 and np.mean(rates) > 0.25)
    return {
        "effect_name": "surprise_driven_readaptation",
        "experiment": "exp0",
        "original_effect_size": 0.25,
        "effect_size": float(np.mean(rates)),
        "p": float(p),
        "t": float(t_stat),
        "swapped_states": swapped,
        "reproduced": reproduced,
    }


def check_reward_learning_over_episodes(data: dict[str, pd.DataFrame]) -> dict:
    """"After the 1st episode, participants had learnt to reach the goal in less than 20 steps
    (episodes 2 to 5 in Fig 1C)." — Xu et al. 2021, Results, p.3. The check: the number of
    actions taken to reach the goal in episode 1 of block 1 is significantly larger than the
    mean number taken in episodes 2-5 of block 1 (paired t-test across participants)."""
    df = data["exp0"]
    steps = df.groupby(["participant_id", "block", "epi"]).size().reset_index(name="n")
    b1 = steps[(steps["block"] == 0)]
    ep1 = b1[b1["epi"] == 1].set_index("participant_id")["n"]
    later = b1[b1["epi"].isin([2, 3, 4, 5])].groupby("participant_id")["n"].mean()
    common = sorted(set(ep1.index) & set(later.index))
    a = ep1.loc[common].to_numpy(float)
    b = later.loc[common].to_numpy(float)
    t_stat, p = stats.ttest_rel(a, b)
    diff = (a - b).mean()
    reproduced = bool(p < 0.05 and diff > 0)
    return {
        "effect_name": "reward_learning_over_episodes",
        "experiment": "exp0",
        "original_effect_size": 98.0,
        "effect_size": float(diff),
        "p": float(p),
        "t": float(t_stat),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_novelty_driven_exploration,
    check_surprise_driven_readaptation,
    check_reward_learning_over_episodes,
]


def run_analysis(sources: Optional[dict[str, str]] = None) -> list[dict]:
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
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()