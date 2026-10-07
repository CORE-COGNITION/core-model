# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "scipy"]
# ///

"""Check the primary behavioral effects of Singh, Richie, & Bhatia (2022), Representing
and Predicting Everyday Behavior, against any dataset in the Psych-301 unified schema.

Effects tested:
- mundane_vs_criminal_propensity (exp0): mundane/common behaviors are rated higher in
  behavioral propensity than dangerous/criminal behaviors (papel's exemplar phrases).
"""
from __future__ import annotations

import argparse
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0"]

MUNDANE = ["access the internet", "sleep in a bed", "spell my name", "consider a question", "reflect on a subject"]
CRIMINAL = ["kill someone", "commit a felony", "suck my thumb", "escape from prison", "condemn someone as a heretic"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def check_mundane_vs_criminal_propensity(data: dict[str, pd.DataFrame]) -> dict:
    """\"Some of these phrases include access the internet, reflect on a subject, consider a
    question, spell my name, and sleep in a bed. ... Some of these phrases include kill
    someone, suck my thumb, commit a felony, escape from prison, and condemn someone as a
    heretic.\" — Singh et al., 2022, p.27 (Results: Summary of Phrase Ratings)."""
    df = data["exp0"].copy()
    df["_phrase"] = df["phrase"].astype(str).str.lower().str.strip()
    mundane = df[df["_phrase"].isin(MUNDANE)]["response"]
    criminal = df[df["_phrase"].isin(CRIMINAL)]["response"]
    stat, p = stats.ttest_ind(mundane, criminal, equal_var=False)
    reproduced = (mundane.mean() > criminal.mean()) and (p < 0.05)
    return {
        "effect_name": "mundane_vs_criminal_propensity",
        "experiment": "exp0",
        "original_effect_size": -1.0,
        "effect_size": float(mundane.mean() - criminal.mean()),
        "mundane_mean": float(mundane.mean()),
        "criminal_mean": float(criminal.mean()),
        "p": float(p),
        "reproduced": bool(reproduced),
    }


EFFECTS = [check_mundane_vs_criminal_propensity]


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
        print(f"{exp}: {sources.get(exp, '(default — local ./%s.csv)' % exp)}")
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
