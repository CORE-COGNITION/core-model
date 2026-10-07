# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Bavard et al. (2018, Nature Communications,
"Reference-point centering and range-adaptation enhance human reinforcement learning at
the cost of irrational preferences") against any dataset in the Psych-301 unified schema.

Effects tested:
- learning_above_chance (exp0, exp1): mean correct choice rate (favorable option chosen)
  across all learning contexts exceeds 0.5; one-sample t-test vs chance, expected positive.
- learning_magnitude_effect (exp0, exp1): correct choice rate is higher in big-magnitude
  than small-magnitude contexts; per-participant big-minus-small difference, expected positive.
- transfer_above_chance (exp0, exp1): in the no-feedback transfer test correct choice rate
  (choosing the option with higher absolute expected value) exceeds 0.5; t-test vs chance.
- transfer_irrational_preference (exp0, exp1): the reward/small favorable option (symbol 3,
  EV +0.075) is chosen more often than the reward/big unfavorable option (symbol 2, EV +0.25)
  => subjectively preferred option has LOWER expected value (irrational, higher magnitude wins).
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0", "exp1"]

# Absolute expected value of each transfer symbol (identity 1..8, from the authors' fitting
# code: symbols 2k-1 / 2k = favorable / unfavorable cue of session-2 context 4+k):
# context1 reward/big: fav +0.75 / unfav +0.25; context2 reward/small: +0.075/+0.025;
# context3 loss/big: -0.25/-0.75; context4 loss/small: -0.025/-0.075.
SYMBOL_EV = {1: 0.75, 2: 0.25, 3: 0.075, 4: 0.025, 5: -0.25, 6: -0.75, 7: -0.025, 8: -0.075}


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}. sources: optional {exp: csv_path} override;
    otherwise reads ./{exp}.csv from CWD."""
    sources = sources or {}
    data = {}
    for exp in EXPERIMENTS:
        df = pd.read_csv(sources.get(exp, f"./{exp}.csv"))
        # Parse only the transfer choice_set column lazily if present.
        df["choice_set_raw"] = df.get("choice_set")
        data[exp] = df
    return data


def _per_ppt_rates(df: pd.DataFrame, correct_mask: pd.Series) -> pd.Series:
    """Mean correct-response rate per participant over the given (already-subset) rows."""
    sub = df.copy()
    sub["correct"] = correct_mask.astype(int)
    return sub.groupby("participant_id")["correct"].mean()


def check_learning_above_chance(data: dict[str, pd.DataFrame]) -> dict:
    """"In all contexts, this average correct response rate was higher than chance level
    0.5, signaling significant instrumental learning effects (T(59)=16.6, P<0.001)" -- Bavard
    et al. 2018, p.3, Results ('Outcome magnitude moderately affects learning')."""
    rates = []
    for exp in EXPERIMENTS:
        lf = data[exp].query("phase == 'learning'").copy()
        rates.append(_per_ppt_rates(lf, lf["response"] == 1))
    rates = pd.concat(rates)
    t, p = stats.ttest_1samp(rates, 0.5)
    reproduced = bool(rates.mean() > 0.5 and p < 0.05)
    return {"effect_name": "learning_above_chance", "experiment": "exp0,exp1",
            "original_effect_size": 16.6, "effect_size": float(t),
            "mean_correct": float(rates.mean()), "p": float(p), "reproduced": reproduced}


def check_learning_magnitude_effect(data: dict[str, pd.DataFrame]) -> dict:
    """"Post-hoc test confirmed that... subjects showed significantly higher correct choice
    rate in the big-magnitude compared with the small-magnitude contexts (T(59)>3.0,
    P<0.004)" -- Bavard et al. 2018, p.3, Results. Magnitude: F(59)=9.091, P=0.0038 (both exps)."""
    diffs = []
    for exp in EXPERIMENTS:
        lf = data[exp].query("phase == 'learning'").copy()
        lf["correct"] = (lf["response"] == 1).astype(int)
        g = lf.groupby(["participant_id", "magnitude"])["correct"].mean().unstack()
        diffs.append(g["big"] - g["small"])
    diffs = pd.concat(diffs)
    t, p = stats.ttest_1samp(diffs, 0.0)
    reproduced = bool(diffs.mean() > 0 and p < 0.05)
    return {"effect_name": "learning_magnitude_effect", "experiment": "exp0,exp1",
            "original_effect_size": np.sqrt(9.091), "effect_size": float(t),
            "mean_diff": float(diffs.mean()), "p": float(p), "reproduced": reproduced}


def check_transfer_above_chance(data: dict[str, pd.DataFrame]) -> dict:
    """"Overall, the correct choice rate in the transfer was significantly higher than chance,
    thus providing evidence of significant value transfer and retrieval (T(59)>3.0,
    P<0.004)" -- Bavard et al. 2018, p.3, Results ('Transfer test choices')."""
    rates = []
    for exp in EXPERIMENTS:
        tr = data[exp].query("phase == 'transfer'").copy()
        chosen_ev = np.where(tr["response"] == 1,
                             tr["stimulus_right"].map(SYMBOL_EV),
                             tr["stimulus_left"].map(SYMBOL_EV))
        best_ev = np.maximum(tr["stimulus_left"].map(SYMBOL_EV),
                             tr["stimulus_right"].map(SYMBOL_EV))
        rates.append(_per_ppt_rates(tr, chosen_ev == best_ev))
    rates = pd.concat(rates)
    t, p = stats.ttest_1samp(rates, 0.5)
    reproduced = bool(rates.mean() > 0.5 and p < 0.05)
    return {"effect_name": "transfer_above_chance", "experiment": "exp0,exp1",
            "original_effect_size": 3.0, "effect_size": float(t),
            "mean_correct": float(rates.mean()), "p": float(p), "reproduced": reproduced}


def _symbol_chosen(row: pd.Series) -> int:
    return int(row["stimulus_right"]) if row["response"] == 1 else int(row["stimulus_left"])


def _symbol_choice_rates(df: pd.DataFrame, symbol: int) -> list[float]:
    tr = df.query("phase == 'transfer'").copy()
    out = {}
    for pid, g in tr.groupby("participant_id"):
        presented = g[(g["stimulus_left"] == symbol) | (g["stimulus_right"] == symbol)]
        chosen = np.array([_symbol_chosen(r) for _, r in presented.iterrows()])
        out[pid] = float(np.mean(chosen == symbol))
    return list(out.values())


def check_transfer_irrational_preference(data: dict[str, pd.DataFrame]) -> dict:
    """"...the favorable option of the reward/small context was chosen more often than the
    less favorable option of the reward/big context (0.71±0.03 vs. 0.41±0.04; T(59)=6.43,
    P<0.0001)" -- Bavard et al. 2018, p.3, Results ('Transfer test choices do not follow
    expected values'). Higher magnitude option (symbol 3, EV +0.075) preferred over higher-EV
    option (symbol 2, EV +0.25): an irrational preference for magnitude over gain probability."""
    s3, s2 = [], []
    for exp in EXPERIMENTS:
        d = data[exp]
        s3 += _symbol_choice_rates(d, 3)
        s2 += _symbol_choice_rates(d, 2)
    s3 = np.array(s3)
    s2 = np.array(s2)
    t, p = stats.ttest_rel(s3, s2)
    reproduced = bool((s3 - s2).mean() > 0 and p < 0.05)
    return {"effect_name": "transfer_irrational_preference", "experiment": "exp0,exp1",
            "original_effect_size": 6.43, "effect_size": float(t),
            "rate_sym3": float(s3.mean()), "rate_sym2": float(s2.mean()),
            "p": float(p), "reproduced": reproduced}


EFFECTS = [
    check_learning_above_chance,
    check_learning_magnitude_effect,
    check_transfer_above_chance,
    check_transfer_irrational_preference,
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
        print(f"{exp}: {sources[exp]}" if exp in sources else f"{exp}: (default -- local ./{exp}.csv)")
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