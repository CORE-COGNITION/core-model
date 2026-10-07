# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Dubois et al. (2022), "Value-free random
exploration is linked to impulsivity" (Nat. Commun. 13:4542), against any dataset in
the Psych-301 unified schema (see schema.md).

Effects tested (all in exp0, all on the first free draw of each game, short-horizon
single draw vs long-horizon first draw, per-participant Wilcoxon signed-rank):
- horizon_exploration_lower_ev (exp0): expected value (mean of the initial samples) of
  the chosen bandit is LOWER in the long horizon — more exploration where it pays off.
- directed_exploration_information (exp0): number of initial samples of the chosen
  bandit is LOWER in the long horizon — choosing bandits one knows less about (more
  informative, goal-directed exploration).
- high_value_bandit_frequency (exp0): frequency of picking the (expected) high-value
  bandit DECREASES in the long horizon — forgoing the best expected outcome.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0"]

TREE_IDS = np.array([1, 2, 3, 4])
TREE_COLS = ["TreeA", "TreeB", "TreeC", "TreeD"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD.

    Required columns for exp0: participant_id, block, response, reward,
    forced_choice, Horizon, TreeLeft, TreeMiddle, TreeRight, TreeA..TreeD.
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _game_features(df: pd.DataFrame) -> pd.DataFrame:
    """Per-game (participant, block) features from the raw trial rows.

    - initial samples per tree: reward on forced_choice==1 rows where that tree's
      TreeX indicator is 1 (count and mean).
    - first free draw: first row with forced_choice==0.
    """
    forced = df[df["forced_choice"] == 1]
    init: pd.DataFrame = pd.DataFrame()
    for t in TREE_COLS:
        sub = forced[forced[t] == 1]
        g = sub.groupby(["participant_id", "block"])["reward"]
        m = pd.concat(
            [g.count().rename(t + "_cnt"), g.mean().rename(t + "_mean")], axis=1
        )
        init = pd.concat([init, m], axis=1)
    init = init.reset_index()

    first = (
        df[df["forced_choice"] == 0]
        .groupby(["participant_id", "block"])
        .first()
        .reset_index()
    )
    game = first.merge(init, on=["participant_id", "block"])

    mean = game[[t + "_mean" for t in TREE_COLS]].to_numpy(float)  # (n,4), id=t+1
    cnt = game[[t + "_cnt" for t in TREE_COLS]].to_numpy(float)
    pos = np.column_stack(
        [game[c].to_numpy(int) - 1 for c in ("TreeLeft", "TreeMiddle", "TreeRight")]
    )
    chosen = np.array(
        [
            int(game[["TreeLeft", "TreeMiddle", "TreeRight"][i]].iat[r])
            - 1
            for r, i in enumerate(game["response"].astype(int))
        ]
    )  # (n,)
    n = len(game)
    idx = np.arange(n)

    game["chosen_ev"] = mean[idx, chosen]
    game["chosen_ns"] = cnt[idx, chosen]

    presented_mean = np.where(np.isnan(mean[idx[:, None], pos]), -np.inf, mean[idx[:, None], pos])
    max_mean = presented_mean.max(axis=1)
    presented_cnt = cnt[idx[:, None], pos]

    # high-value bandit: presented tree with the highest initial-sample mean
    is_hv = presented_mean == max_mean[:, None]
    hv_any = is_hv.max(axis=1)
    hv_chosen = (chosen[:, None] == pos) & is_hv
    game["chose_hv"] = hv_chosen.any(axis=1).astype(int)
    game["hv_present"] = hv_any

    # low-value bandit: presented tree with exactly one initial sample and the
    # smallest value among those (the low-value initial sample is the smallest)
    single = presented_cnt == 1
    min_single = np.where(single, presented_mean, np.inf).min(axis=1)
    is_lv = single & (presented_mean == min_single[:, None])
    lv_chosen = (chosen[:, None] == pos) & is_lv
    game["chose_lv"] = lv_chosen.any(axis=1).astype(int)
    game["lv_present"] = single.any(axis=1)

    game["short"] = game["Horizon"].eq(6)
    return game


def _wilcoxon_subject(game: pd.DataFrame, col: str, long_gt_short: bool) -> dict:
    """Per-participant means by horizon, Wilcoxon signed-rank, direction check."""
    agg = game.groupby(["participant_id", "short"])[col].mean().unstack()
    short, long = agg[True], agg[False]
    stat, p = stats.wilcoxon(short, long, zero_method="wilcox")
    z = stats.norm.ppf(1 - max(p, 1e-15) / 2)
    r = abs(z) / np.sqrt(len(short))
    diff = long.mean() - short.mean()
    sign_ok = (diff > 0) == long_gt_short
    return {
        "short_mean": float(short.mean()),
        "long_mean": float(long.mean()),
        "diff": float(diff),
        "p": float(p),
        "r": float(r),
        "sign_ok": bool(sign_ok),
    }


def check_horizon_exploration_lower_ev(data: dict[str, pd.DataFrame]) -> dict:
    """\"participants chose bandits with a lower expected value ... in the long horizon
    compared to the short horizon, a sign of increased exploration\" — Dubois et al.
    2022, p.2, Results Step 1.1 (V=110057, p<0.001, r=0.265)."""
    game = _game_features(data["exp0"])
    res = _wilcoxon_subject(game[game["chosen_ev"].notna()], "chosen_ev", long_gt_short=False)
    reproduced = res["sign_ok"] and res["p"] < 0.05
    return {
        "effect_name": "horizon_exploration_lower_ev",
        "experiment": "exp0",
        "original_effect_size": 0.265,
        "effect_size": res["r"],
        "reproduced": reproduced,
        "mean_diff_long_minus_short": res["diff"],
        "p": res["p"],
    }


def check_directed_exploration_information(data: dict[str, pd.DataFrame]) -> dict:
    """\"participants choosing bandits they knew less about (lower number of initial
    samples, i.e., more informative) in the long horizon\" — Dubois et al. 2022, p.2,
    Results Step 1.1 (V=160109.5, p<0.001, r=0.796)."""
    game = _game_features(data["exp0"])
    res = _wilcoxon_subject(game, "chosen_ns", long_gt_short=False)
    reproduced = res["sign_ok"] and res["p"] < 0.05
    return {
        "effect_name": "directed_exploration_information",
        "experiment": "exp0",
        "original_effect_size": 0.796,
        "effect_size": res["r"],
        "reproduced": reproduced,
        "mean_diff_long_minus_short": res["diff"],
        "p": res["p"],
    }


def check_high_value_bandit_frequency(data: dict[str, pd.DataFrame]) -> dict:
    """\"We found a reduced frequency of picking the high-value bandit in the long
    horizon\" — Dubois et al. 2022, p.2, Results Step 1.1 (V=157079.5, p<0.001,
    r=0.797)."""
    game = _game_features(data["exp0"])
    game = game[game["hv_present"]]
    res = _wilcoxon_subject(game, "chose_hv", long_gt_short=False)
    reproduced = res["sign_ok"] and res["p"] < 0.05
    return {
        "effect_name": "high_value_bandit_frequency",
        "experiment": "exp0",
        "original_effect_size": 0.797,
        "effect_size": res["r"],
        "reproduced": reproduced,
        "mean_diff_long_minus_short": res["diff"],
        "p": res["p"],
    }


EFFECTS = [
    check_horizon_exploration_lower_ev,
    check_directed_exploration_information,
    check_high_value_bandit_frequency,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. No printing."""
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