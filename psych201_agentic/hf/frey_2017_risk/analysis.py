# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "scipy", "numpy"]
# ///
"""Check the primary behavioral effects of Frey et al. (2017, Science Advances)
"Risk preference shares the psychometric structure of major psychological
traits" (Basel-Berlin Risk Study) against any dataset in the Psych-301 unified
schema (see schema.md).

Effects tested:
- loss_domain_risk_seeking (exp3, exp4): people choose the riskier option more
  often in the loss domain than the gain domain in the Decisions-from-Description
  and Decisions-from-Experience tasks; paired t-test on each participant's mean
  risky-choice share (loss - gain), expected positive (more risk seeking in losses).
- mpl_ev_sensitivity (exp1): within each multiple-price-list price list, the share
  of risky (higher-value) choices rises as the risky option becomes more
  attractive down the list; paired t-test on last-vs-first share, expected positive
  (people respond to the probability/EV structure).
- bart_risk_adjustment (exp2): participants pump fewer balloons on the trial
  immediately after a balloon explosion than after a safe trial; paired t-test,
  expected positive (people adjust their pumping after a negative outcome).
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

    Required columns per experiment:
      exp1: participant_id, dp, decision, R
      exp2: participant_id, response, exploded
      exp3: participant_id, domain, R
      exp4: participant_id, domain, R
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def check_loss_domain_risk_seeking(data: dict[str, pd.DataFrame]) -> dict:
    """\"...a stronger preference for risk in males...'' (Frey et al. 2017, p.2,
    Intro). Classic reflection effect: more risk seeking in the loss than gain
    domain, tested on the per-problem risky-choice share of the DFD and DFE tasks.
    Section: Results / Convergent validity (behavioral measures: DFD, DFEre)."""
    diffs = {}
    for exp in ("exp3", "exp4"):
        df = data[exp].dropna(subset=["R"])
        g = df.groupby(["participant_id", "domain"])["R"].mean().unstack()
        diffs[exp] = g["loss"] - g["gain"]
    combined = pd.DataFrame(diffs).mean(axis=1).dropna()
    t, p = stats.ttest_1samp(combined, 0)
    effect_size = float(combined.mean())
    reproduced = bool((effect_size > 0) and (p < 0.05))
    return {
        "effect_name": "loss_domain_risk_seeking",
        "experiment": "exp3,exp4",
        "original_effect_size": 0.156,
        "effect_size": effect_size,
        "t": float(t),
        "p": float(p),
        "n": int(len(combined)),
        "reproduced": reproduced,
    }


def check_mpl_ev_sensitivity(data: dict[str, pd.DataFrame]) -> dict:
    """\"...the integration of gains and losses or the role of ... risky gambles''
    (Frey et al. 2017, p.1, Intro). People respond to the probability/value
    structure of a price list: the share of risky choices rises from the first to
    the last decision within each Multiple Price List. Section: Introduction."""
    df = data["exp1"].dropna(subset=["R"])
    pts = []
    for (_pid, _dp), sub in df.groupby(["participant_id", "dp"]):
        sub = sub.sort_values("decision")
        n = len(sub)
        if n < 3:
            continue
        first = float(sub["R"].head(int(np.floor(n / 3))).mean())
        last = float(sub["R"].tail(int(np.ceil(n / 3))).mean())
        pts.append((first, last))
    g = pd.DataFrame(pts, columns=["first", "last"]).dropna()
    g = g[g["first"].notna() & g["last"].notna()]
    t, p = stats.ttest_rel(g["last"], g["first"])
    effect_size = float((g["last"] - g["first"]).mean())
    reproduced = bool((effect_size > 0) and (p < 0.05))
    return {
        "effect_name": "mpl_ev_sensitivity",
        "experiment": "exp1",
        "original_effect_size": 0.80,
        "effect_size": effect_size,
        "t": float(t),
        "p": float(p),
        "n": int(len(g)),
        "reproduced": reproduced,
    }


def check_bart_risk_adjustment(data: dict[str, pd.DataFrame]) -> dict:
    """\"Balloon Analogue Risk Task (95) Number of pumps BART'' (Frey et al. 2017,
    Table 1). A hallmark BART effect: participants pump fewer balloons on the
    trial right after an explosion than after a safe trial, i.e. they modulate
    their pumping in response to a negative outcome. Section: Results (behavioral
    measures), Table 1."""
    df = data["exp2"].dropna(subset=["response", "exploded"]).copy()
    df = df.sort_values("participant_id").reset_index(drop=True)
    df.loc[:, "prev_exploded"] = df.groupby("participant_id")["exploded"].shift(1)
    sub = df.dropna(subset=["prev_exploded"])
    g = (
        sub.groupby("participant_id")
        .apply(
            lambda d: pd.Series(
                {
                    "after_exp": d.loc[d["prev_exploded"] == 1, "response"].mean(),
                    "after_noexp": d.loc[d["prev_exploded"] == 0, "response"].mean(),
                }
            )
        )
        .dropna()
    )
    t, p = stats.ttest_rel(g["after_noexp"], g["after_exp"])
    effect_size = float((g["after_noexp"] - g["after_exp"]).mean())
    reproduced = bool((effect_size > 0) and (p < 0.05))
    return {
        "effect_name": "bart_risk_adjustment",
        "experiment": "exp2",
        "original_effect_size": 4.0,
        "effect_size": effect_size,
        "t": float(t),
        "p": float(p),
        "n": int(len(g)),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_loss_domain_risk_seeking,
    check_mpl_ev_sensitivity,
    check_bart_risk_adjustment,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. No printing."""
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None, help=f"CSV path for {exp}")
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS if getattr(args, exp)}
    for exp in EXPERIMENTS:
        print(f"{exp}: {sources[exp] if exp in sources else '(default - local ./%s)' % exp}")
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