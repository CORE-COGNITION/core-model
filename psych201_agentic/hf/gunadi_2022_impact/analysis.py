# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Gunadi & Evangelidis (2022), "The Impact of
Historical Price Information on Purchase Deferral" (JMR), against any dataset in the
Psych-301 unified schema (see schema.md).

Effects tested:
- direction_effect_single (exp0/Study 1a): on a single historical price change, deferral
  (P(buy later)) is higher after a price increase than after a decrease  (chi-square).
- frequency_moderation_direction (exp0/Study 1a): the increase-minus-decrease gap in
  deferral is larger for a single change than for multiple changes (logistic interaction).
- direction_effect_single_consequential (exp5/Study 5): with real purchase decisions on a
  single change, increase > decrease deferral (chi-square).

response is coded 0 = buy now, 1 = defer (buy later). Direction: inc_* = price increased,
dec_* = price decreased. Frequency: single = one change, multiple = several changes.
"""
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd
import scipy.stats as st
import statsmodels.formula.api as smf

EXPERIMENTS = ["exp0", "exp5"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides, loads
    ./{exp}.csv from CWD — cd into a checkout of the dataset repo (or pass --<exp> path
    on the CLI) before running.

    Required columns:
      exp0: participant_id, trial, response, condition
      exp5: participant_id, trial, response, condition
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _chisq(a, b):
    """chi-square test of deferral rate between two conditions. Returns (diff, p, n1, n2)."""
    t = pd.DataFrame({
        "y": np.concatenate([a["response"], b["response"]]),
        "g": np.concatenate([np.zeros(len(a), dtype=int), np.ones(len(b), dtype=int)]),
    })
    ctab = pd.crosstab(t["g"], t["y"])
    chi2, p, _, _ = st.chi2_contingency(ctab, correction=False)
    return (b["response"].mean() - a["response"].mean()), p, len(a), len(b)


def check_direction_effect_single(data: dict[str, pd.DataFrame]) -> dict:
    """\"When participants observed a single change in price, they were much more likely to
    defer purchase when the price had previously increased (53.7%) compared to when the price
    had decreased (9.5%), Wald chi2 = 74.28, p < .001.\" — Gunadi & Evangelidis 2022,
    p.15, Study 1a."""
    df = data["exp0"]
    inc = df[df["condition"] == "inc_single"]
    dec = df[df["condition"] == "dec_single"]
    diff, p, n1, n2 = _chisq(dec, inc)
    return {
        "effect_name": "direction_effect_single",
        "experiment": "exp0",
        "original_effect_size": 0.537 - 0.095,
        "effect_size": diff,
        "p": p,
        "n": (n1, n2),
        "reproduced": bool(diff > 0 and p < 0.05),
    }


def check_frequency_moderation_direction(data: dict[str, pd.DataFrame]) -> dict:
    """\"Consistent with H1... the predicted interaction between the direction and frequency
    of price changes on purchase deferral was statistically significant (Wald chi2 = 49.88,
    p < .001).\" — Gunadi & Evangelidis 2022, p.15, Study 1a."""
    df = data["exp0"].copy()
    df["direction"] = df["condition"].str.startswith("inc").astype(int)
    df["frequency"] = df["condition"].str.contains("multiple").astype(int)
    m = smf.logit("response ~ direction + frequency + direction:frequency", data=df).fit(disp=0)
    coef = m.params["direction:frequency"]
    p = m.pvalues["direction:frequency"]
    return {
        "effect_name": "frequency_moderation_direction",
        "experiment": "exp0",
        "original_effect_size": -2.9,
        "effect_size": coef,
        "p": p,
        "n": len(df),
        "reproduced": bool(np.sign(coef) == -1 and p < 0.05),
    }


def check_direction_effect_single_consequential(data: dict[str, pd.DataFrame]) -> dict:
    """\"Across products, upon observing a single change in price, participants were much more
    likely to defer purchase when the price had previously increased (88.9%) compared to when
    the price had decreased (49.5%), Wald chi2 = 82.71, p < .001.\" — Gunadi & Evangelidis
    2022, p.30, Study 5."""
    df = data["exp5"]
    inc = df[df["condition"] == "inc_single"]
    dec = df[df["condition"] == "dec_single"]
    diff, p, n1, n2 = _chisq(dec, inc)
    return {
        "effect_name": "direction_effect_single_consequential",
        "experiment": "exp5",
        "original_effect_size": 0.889 - 0.495,
        "effect_size": diff,
        "p": p,
        "n": (n1, n2),
        "reproduced": bool(diff > 0 and p < 0.05),
    }


EFFECTS = [
    check_direction_effect_single,
    check_frequency_moderation_direction,
    check_direction_effect_single_consequential,
]


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
