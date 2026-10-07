# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Anvari et al. (2024), "Testing the
convergent validity, domain generality, and temporal stability of selected
measures of people's tendency to explore" (Nat. Commun. 15:7721), against any
dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- bandit_within_task_convergence (exp0): participants who switch arms more
  (higher switch rate) also exploit the best arm less (higher exploit
  complement); two exploration measures in the multi-armed bandit are
  positively correlated (Pearson r, one-sided). Expected r > 0, p < .05.
- alien_within_task_convergence (exp4): participants who explore more
  (higher active-search rate) also search farther from the best prior
  combination (higher Hamming distance) in the alien game; two exploration
  measures derived from the same task positively correlate. Expected r > 0,
  p < .05.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0", "exp1", "exp2", "exp3", "exp4"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD.

    Required columns:
      exp0: participant_id, task_id, phase, trial, response,
            player_bandit_1_average_payoff..player_bandit_5_average_payoff
            (session is used as a block key when present)
      exp4: participant_id, task_id, phase, trial, response (10-digit bit
            string), player_landscape_payoff (forced_choice and session are used
            when present)
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv"), low_memory=False,
                             dtype={"response": str} if exp == "exp4" else None)
            for exp in EXPERIMENTS}


def _block_keys(df: pd.DataFrame) -> list[str]:
    return [c for c in ("participant_id", "session", "task_id") if c in df.columns]


def check_bandit_within_task_convergence(data: dict[str, pd.DataFrame]) -> dict:
    """In sum, the only behavioural measures of exploration that had evidence of
    some convergent validity ... were ... the 2 pairs of measures derived from
    the same task (i.e., switch rate and exploit-complement, both in bandit
    task, ...)" — Anvari et al., 2024, p.5, Results (Hypothesis 1).

    Both measures are computed within each incentivized block (Methods, p. 14):
    a switch is a choice that differs from the previous trial's choice, and
    exploiting is choosing the arm with the highest average payoff so far, i.e.
    the averages displayed after the previous trial (the average columns of a
    row already include that row's payoff)."""
    df = data["exp0"]
    df = df[df["phase"] == "test"].copy()
    keys = _block_keys(df)
    df = df.sort_values(keys + ["trial"], kind="mergesort")
    bandit_cols = [f"player_bandit_{i}_average_payoff" for i in range(1, 6)]
    grp = df.groupby(keys, sort=False)
    df["prev_choice"] = grp["response"].shift(1)
    prev_avg = grp[bandit_cols].shift(1)
    df["prev_best"] = prev_avg.to_numpy().argmax(axis=1)
    df = df[df["prev_choice"].notna()]
    df["switch"] = (df["response"] != df["prev_choice"]).astype(int)
    df["chose_best"] = (df["response"].to_numpy() == df["prev_best"].to_numpy()).astype(int)
    g = df.groupby("participant_id").agg(
        switch_rate=("switch", "mean"),
        exploit_comp=("chose_best", lambda x: 1.0 - x.mean()),
    )
    r, p = stats.pearsonr(g["switch_rate"], g["exploit_comp"])
    reproduced = bool(r > 0 and p < 0.05)
    return {
        "effect_name": "bandit_within_task_convergence",
        "experiment": "exp0",
        "original_effect_size": 0.47,
        "effect_size": float(r),
        "p_value": float(p),
        "reproduced": reproduced,
    }


def _alien_measures(block: pd.DataFrame) -> tuple[list[int], list[int]]:
    """Per free trial of one block: Hamming distance to the most recent
    best-paying earlier combination, and 1 if the combination is new (Methods,
    p. 14; the displayed starting combination counts as an earlier one)."""
    hamming, active = [], []
    best, best_pay, seen = None, -np.inf, []
    forced = block["forced_choice"].to_numpy() if "forced_choice" in block.columns else np.zeros(len(block))
    for combo, pay, fc in zip(block["response"].astype(str), block["player_landscape_payoff"], forced):
        if best is not None and fc != 1:
            hamming.append(sum(a != b for a, b in zip(combo, best)))
            active.append(int(combo not in seen))
        seen.append(combo)
        if pay >= best_pay:
            best, best_pay = combo, pay
    return hamming, active


def check_alien_within_task_convergence(data: dict[str, pd.DataFrame]) -> dict:
    """In sum, the only behavioural measures of exploration that had evidence
    of some convergent validity ... were ... the 2 pairs of measures derived
    from the same task (i.e., ... Hamming distance and active search, both in
    the alien game)" — Anvari et al., 2024, p.5, Results (Hypothesis 1)."""
    df = data["exp4"]
    df = df[df["phase"] == "test"].copy()
    keys = _block_keys(df)
    df = df.sort_values(keys + ["trial"], kind="mergesort")
    per_pid: dict = {}
    for k, block in df.groupby(keys, sort=False):
        pid = k[0] if isinstance(k, tuple) else k
        h, a = _alien_measures(block)
        per_pid.setdefault(pid, ([], []))
        per_pid[pid][0].extend(h)
        per_pid[pid][1].extend(a)
    g = pd.DataFrame({"hamming": [np.mean(v[0]) for v in per_pid.values()],
                      "active": [np.mean(v[1]) for v in per_pid.values()]})
    r, p = stats.pearsonr(g["hamming"], g["active"])
    reproduced = bool(r > 0 and p < 0.05)
    return {
        "effect_name": "alien_within_task_convergence",
        "experiment": "exp4",
        "original_effect_size": 0.52,
        "effect_size": float(r),
        "p_value": float(p),
        "reproduced": reproduced,
    }


EFFECTS = [check_bandit_within_task_convergence, check_alien_within_task_convergence]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. No printing."""
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None, help=f"CSV path for {exp}; defaults to ./{exp}.csv")
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS if getattr(args, exp)}
    for exp in EXPERIMENTS:
        print(f"{exp}: {sources[exp] if exp in sources else '(default - local ./%s.csv)' % exp}")
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
