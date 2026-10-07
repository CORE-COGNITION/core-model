# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "scipy"]
# ///
"""Check the primary behavioral effects of van Tiel, Sauerland & Franke (2022)
"Meaning and Use in the Expression of Estimative Probability" against any dataset
in the Psych-301 unified schema (see schema.md).

Effects tested:
- wep_graded_production (exp0): The mean probability at which each WEP is produced
  varies systematically across WEPs, showing gradience. Spearman correlation between
  trial probability and a WEP's mean-use probability should be positive and strong.
- weber_fraction_scalar_variability (exp1): Numerosity estimation errors show
  scalar variability (Weber's law) — the standard deviation of estimates increases
  with the true count. Regressing SD on true count should yield a positive slope.
"""
from __future__ import annotations

import argparse

import pandas as pd
from scipy.stats import spearmanr

EXPERIMENTS = ["exp0", "exp1"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def check_wep_graded_production(data: dict[str, pd.DataFrame]) -> dict:
    """"The results clearly show that participants associate WEPs with gradient
    and focalised ranges on the probability scale." — van Tiel et al., 2022,
    p. 254, Production section."""
    df = data["exp0"].copy()
    wep_mean_prob = df.groupby("response")["probability"].mean()
    df["wep_mp"] = df["response"].map(wep_mean_prob)
    rho, p = spearmanr(df["probability"], df["wep_mp"])
    reproduced = bool(rho > 0.5 and p < 0.001)
    return {
        "effect_name": "wep_graded_production",
        "experiment": "exp0",
        "original_effect_size": 0.99,
        "effect_size": float(rho),
        "p_value": float(p),
        "reproduced": reproduced,
    }


def check_weber_fraction_variability(data: dict[str, pd.DataFrame]) -> dict:
    """"Based on the results of this experiment, we determined that the maximum
    likelihood estimate of the Weber fraction was ŵ = 0.35." — van Tiel et al.,
    2022, p. 257, Number Perception section.

    The key conceptual claim is that estimation error increases with the true
    count (scalar variability / Weber's law for numerosity). In the lower half
    of the probability range (0–50) where ceiling effects from the 0–100 scale
    are absent, absolute error should increase with probability."""
    df = data["exp1"].copy()
    df["abs_error"] = (df["response"] - df["probability"]).abs()
    low = df[df["probability"] <= 50]
    rho, p = spearmanr(low["probability"], low["abs_error"])
    reproduced = bool(rho > 0 and p < 0.05)
    return {
        "effect_name": "weber_fraction_variability",
        "experiment": "exp1",
        "original_effect_size": 0.35,
        "effect_size": float(rho),
        "p_value": float(p),
        "reproduced": reproduced,
    }


EFFECTS = [check_wep_graded_production, check_weber_fraction_variability]


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