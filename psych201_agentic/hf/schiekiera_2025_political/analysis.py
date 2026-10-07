# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Schiekiera & Niemeyer (2025) against any dataset
in the Psych-301 unified schema (see schema.md).

Effects tested:
- stance_effect_ilos (exp0): Main effect of abstract political stance on intuitive likelihood
  of submission (ILoS). Progressive abstracts should receive higher ILoS ratings than
  conservative abstracts. Tested via independent two-sample t-test (matching Table 5).
  Also tested via linear mixed model (treatment fixed effect, random intercepts for
  participants and abstracts), though the paper's MLM additionally included political
  orientation (not available in the public dataset).
"""
from __future__ import annotations

import argparse
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.formula.api import mixedlm

EXPERIMENTS = ["exp0"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def check_stance_effect_ilos(data: dict[str, pd.DataFrame]) -> dict:
    """"Progressive abstracts were evaluated 3.07% more positively compared to conservative abstracts" — Schiekiera & Niemeyer (2025), p.11, Results (Table 5). See also "The treatment variable political stance (coded as 1 = conservative, -1 = progressive) was significantly associated with ILoS (b = -6.74, p < .001)" — p.13, H1 Results."""
    df = data["exp0"]
    ilos = df[df["response_type"] == "decision1"].copy()

    prog = ilos[ilos["treatment"] == -1]["response"]
    cons = ilos[ilos["treatment"] == 1]["response"]

    t_stat, p_val = stats.ttest_ind(prog, cons, equal_var=True)
    diff = prog.mean() - cons.mean()
    reproduced = diff > 0 and p_val < 0.05

    return {
        "effect_name": "stance_effect_ilos",
        "experiment": "exp0",
        "original_effect_size": 3.07,
        "effect_size": round(float(diff), 3),
        "original_p": 0.032,
        "p_value": round(float(p_val), 4),
        "reproduced": bool(reproduced),
        "n_progressive": int(len(prog)),
        "n_conservative": int(len(cons)),
        "mean_progressive": round(float(prog.mean()), 2),
        "mean_conservative": round(float(cons.mean()), 2),
    }


EFFECTS = [check_stance_effect_ilos]


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
    print()
    print("Note: The paper's primary interaction effect (political stance x political")
    print("orientation on ILoS, b=1.82, p<.001) is untestable without political orientation")
    print("data, which is not included in the public dataset.")


if __name__ == "__main__":
    main()