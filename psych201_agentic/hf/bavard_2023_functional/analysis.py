# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Bavard & Palminteri (2023), "The functional
form of value normalization in human reinforcement learning" (eLife 12:e83891), against
any dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- anti_divisive_set_size (exp0/Experiment 1): In the transfer phase, the choice rate of
  the high-value options from the TRINARY learning contexts (WT86, NT50) is higher than
  that of the high-value options from the BINARY contexts (WB86, NB50). Paired t-test,
  expected positive (contradicts the divisive prediction of a negative set-size effect).
- range_wide_over_narrow (exp0/Experiment 1): In the transfer phase, the choice rate of
  the high-value options from the WIDE contexts (WT86, WB86) is higher than that of the
  high-value options from the NARROW contexts (NT50, NB50). Paired t-test, expected
  positive.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0"]

# Option id -> mean outcome value, for Experiment 1 (exp0).
# Contexts: 1 WT(86,50,14), 2 WB(86,14), 3 NT(50,32,14), 4 NB(50,14).
OPTION_VALUE = {1: 86, 2: 50, 3: 14, 4: 86, 5: 14, 6: 50, 7: 32, 8: 14, 9: 50, 10: 14}


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides, loads
    ./{exp}.csv from CWD.

    Required columns per experiment:
      exp0: participant_id, phase, trial, response, left_option, middle_option,
            right_option
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _transfer_choice_rate(df: pd.DataFrame) -> dict[int, pd.DataFrame]:
    """Return {option_id: per-participant transfer choice rate Series} for Options 1-10.

    Choice rate = (# of transfer trials in which the option is chosen) /
                  (# of transfer trials in which the option is presented).
    """
    t = df[df["phase"] == "transfer"].copy()
    out = {}
    for option in range(1, 11):
        chosen = t.apply(
            lambda r: (r["left_option"] == option and r["response"] == 0)
            or (r["middle_option"] == option and r["response"] == 1)
            or (r["right_option"] == option and r["response"] == 2),
            axis=1,
        )
        present = t.apply(
            lambda r: (r["left_option"] == option)
            or (r["middle_option"] == option)
            or (r["right_option"] == option),
            axis=1,
        )
        c = chosen.groupby(t["participant_id"]).sum()
        p = present.groupby(t["participant_id"]).sum()
        out[option] = c / (p.replace(0, np.nan))
    return out


def _paired_effect(rates: dict[int, pd.DataFrame], high_a, high_b) -> tuple[float, float]:
    """Per-participant mean choice rate of options in `high_a` minus options in `high_b`;
    returns (mean difference, p-value from paired t-test)."""
    a = sum(rates[o] for o in high_a) / len(high_a)
    b = sum(rates[o] for o in high_b) / len(high_b)
    diff = a - b
    t, p = stats.ttest_rel(a, b)
    return float(diff.mean()), float(p)


def check_anti_divisive_set_size(data: dict[str, pd.DataFrame]) -> dict:
    """\"...the higher choice rate for the high-value options in the trinary contexts
    (NT50 and WT86) compared to the binary contexts (NB50 and WB86; t(149) = 4.11, p<0.0001,
    d = 0.34)\" — Bavard & Palminteri (2023), p.6, Results / Behavioral results"""
    rates = _transfer_choice_rate(data["exp0"])
    # Trinary high-value options: WT86=1, NT50=6 ; Binary high-value: WB86=4, NB50=9
    diff_mean, p = _paired_effect(rates, high_a=[1, 6], high_b=[4, 9])
    reproduced = diff_mean > 0 and p < 0.05
    return {
        "effect_name": "anti_divisive_set_size",
        "experiment": "exp0",
        "original_effect_size": 0.34,  # Cohen's d (t(149)=4.11)
        "effect_size": diff_mean,      # mean trinary-minus-binary transfer choice rate
        "p_value": p,
        "reproduced": reproduced,
    }


def check_range_wide_over_narrow(data: dict[str, pd.DataFrame]) -> dict:
    """\"...high-value options in the narrow contexts (NB50 and NT50) displayed a lower
    choice rate compared to the high-value options of the wide contexts (WB86 and WT86;
    t(49) = -4.19, p = 0.00011, d = -0.72)\" — Bavard & Palminteri (2023), p.6, Results /
    Behavioral results"""
    rates = _transfer_choice_rate(data["exp0"])
    # Wide high-value: WT86=1, WB86=4 ; Narrow high-value: NT50=6, NB50=9
    diff_mean, p = _paired_effect(rates, high_a=[1, 4], high_b=[6, 9])
    reproduced = diff_mean > 0 and p < 0.05
    return {
        "effect_name": "range_wide_over_narrow",
        "experiment": "exp0",
        "original_effect_size": -0.72,  # Cohen's d (wide-narrow, as reported narrow-vs-wide)
        "effect_size": diff_mean,       # mean wide-minus-narrow transfer choice rate
        "p_value": p,
        "reproduced": reproduced,
    }


EFFECTS = [check_anti_divisive_set_size, check_range_wide_over_narrow]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. No printing — pure return value."""
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None, help=f"CSV path for {exp}; defaults to ./{exp}.csv in CWD")
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS if getattr(args, exp)}
    for exp in EXPERIMENTS:
        print(f"{exp}: {sources[exp] if exp in sources else '(default — local ./{exp}.csv)'}")
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
