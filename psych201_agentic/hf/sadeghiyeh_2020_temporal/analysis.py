# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Sadeghiyeh et al. (2020), "Temporal discounting
correlates with directed exploration but not with random exploration", Scientific Reports,
against any dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- directed_exploration_discounting (exp0+exp1): Pearson correlation between log(overall k)
  and directed exploration (change in p(high info) from horizon 1 to horizon 6);
  expected NEGATIVE and significant.
- random_exploration_discounting (exp0+exp1): Pearson correlation between log(overall k)
  and random exploration (change in p(low mean) from horizon 1 to horizon 6);
  expected NULL (no significant relationship).
- uncertainty_seeking_h1_discounting (exp0+exp1): Pearson correlation between log(overall k)
  and p(high info) at horizon 1 (uncertainty preference in the [1 3] condition);
  expected POSITIVE and significant.
"""
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0", "exp1"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD.

    Required columns:
      exp0: participant_id, task_id, trial, horizon, forced_choice, response, reward
      exp1: participant_id, overall_k
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def first_free_stats(horizon_df: pd.DataFrame) -> pd.DataFrame:
    """Per (participant, game) first free choice, horizon, info condition and option labels.

    Horizon Task per game: 4 forced trials then free trials. For each game we take only the
    first free choice. The [1 3] (unequal) info condition has one bandit forced 3x and the
    other 1x; the option forced 1x is the high-information/uncertain option. The [2 2]
    (equal) condition forces each option twice. p(low mean) is defined in the equal condition
    as the chance of picking the bandit whose forced draws paid less on average (as in the
    paper's main.m); equal-condition games where both bandits paid the same are skipped.
    """
    rows = []
    for (pid, gid), g in horizon_df.groupby(["participant_id", "task_id"]):
        free = g[g["forced_choice"] == 0]
        if len(free) == 0:
            continue
        fr = free.iloc[0]
        forced = g[g["forced_choice"] == 1]
        fseq = forced["response"].tolist()
        nA = fseq.count(0)
        nB = fseq.count(1)
        if nA == 2 and nB == 2:
            icond = "equal"
            hi = None
        else:
            icond = "unequal"
            hi = 0 if nA == 1 else 1  # option forced once = high-information option
        avA = forced.loc[forced["response"] == 0, "reward"].mean()
        avB = forced.loc[forced["response"] == 1, "reward"].mean()
        lowmean = None if avA == avB else (0 if avA < avB else 1)
        rows.append(dict(pid=int(pid), gid=int(gid), horizon=int(fr["horizon"]),
                         icond=icond, resp=int(fr["response"]), hi=hi, lowmean=lowmean))
    return pd.DataFrame(rows)


def participant_measures(data: dict[str, pd.DataFrame]) -> tuple[pd.Series, dict]:
    """Returns (log overall k per participant, dict of per-participant task measures)."""
    exp0 = data["exp0"]
    exp1 = data["exp1"]
    k = exp1.groupby("participant_id")["overall_k"].first()
    lk = np.log(k)
    res = first_free_stats(exp0)
    res = res[res["pid"].isin(lk.index)]
    measures = {}
    for h in (1, 6):
        ui = res.loc[(res["horizon"] == h) & (res["icond"] == "unequal")].groupby("pid")
        measures[f"hi{h}"] = ui.apply(lambda s: float((s["resp"] == s["hi"]).mean()))
        eq = res.loc[(res["horizon"] == h) & (res["icond"] == "equal")
                     & res["lowmean"].notna()].groupby("pid")
        measures[f"lm{h}"] = eq.apply(lambda s: float((s["resp"] == s["lowmean"]).mean()))
    return lk, measures


def _corr(lk: pd.Series, s: pd.Series) -> tuple[float, float, int]:
    d = pd.concat([lk, s.reindex(lk.index)], axis=1).dropna()
    if len(d) < 10:
        return np.nan, 1.0, len(d)
    r, p = stats.pearsonr(d.iloc[:, 0], d.iloc[:, 1])
    return float(r), float(p), len(d)


def check_directed_exploration_discounting(data: dict[str, pd.DataFrame]) -> dict:
    """\"We found a significant negative correlation between temporal discounting and
    directed exploration, with more temporal discounting associated with less directed
    exploration.\" — Sadeghiyeh et al., 2020, p.6, Results (Table 3: r = -0.30, p = 0.007)."""
    lk, m = participant_measures(data)
    directed = m["hi6"] - m["hi1"]
    r, p, n = _corr(lk, directed)
    reproduced = bool((r < 0) and (p < 0.05) and n >= 30)
    return {
        "effect_name": "directed_exploration_discounting",
        "experiment": "exp0+exp1",
        "original_effect_size": -0.30,
        "effect_size": r,
        "p_value": p,
        "n": n,
        "reproduced": reproduced,
    }


def check_random_exploration_discounting(data: dict[str, pd.DataFrame]) -> dict:
    """\"In contrast to directed exploration, temporal discounting did not correlate with
    random exploration.\" — Sadeghiyeh et al., 2020, p.6, Results (Table 3: r = 0.04, p = 0.720)."""
    lk, m = participant_measures(data)
    rand = m["lm6"] - m["lm1"]
    r, p, n = _corr(lk, rand)
    reproduced = bool((p >= 0.05) and (abs(r) < 0.2) and n >= 30)
    return {
        "effect_name": "random_exploration_discounting",
        "experiment": "exp0+exp1",
        "original_effect_size": 0.04,
        "effect_size": r,
        "p_value": p,
        "n": n,
        "reproduced": reproduced,
    }


def check_uncertainty_seeking_h1_discounting(data: dict[str, pd.DataFrame]) -> dict:
    """\"...this negative correlation was driven by a positive correlation between temporal
    discounting and p(high info) at horizon 1 and a zero correlation between temporal
    discounting and p(high info) at horizon 6.\" — Sadeghiyeh et al., 2020, p.6, Results
    (Table 3: p(high info) h1 r = 0.35, p = 0.001)."""
    lk, m = participant_measures(data)
    r, p, n = _corr(lk, m["hi1"])
    reproduced = bool((r > 0) and (p < 0.05) and n >= 30)
    return {
        "effect_name": "uncertainty_seeking_h1_discounting",
        "experiment": "exp0+exp1",
        "original_effect_size": 0.35,
        "effect_size": r,
        "p_value": p,
        "n": n,
        "reproduced": reproduced,
    }


EFFECTS = [
    check_directed_exploration_discounting,
    check_random_exploration_discounting,
    check_uncertainty_seeking_h1_discounting,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. Pure return value."""
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None, help=f"CSV path for {exp}; defaults to ./{exp}.csv in CWD")
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS if getattr(args, exp)}
    for exp in EXPERIMENTS:
        print(f"{exp}: {sources[exp]}" if exp in sources else f"{exp}: (default - local ./{exp}.csv)")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<8}  {'orig':>10}  {'this':>10}  {'p':>8}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<8}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{r.get('p_value', float('nan')):>8.4f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()
