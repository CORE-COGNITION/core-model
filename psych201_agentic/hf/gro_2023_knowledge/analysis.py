# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Gross, Kreis, Blank, & Pachur (2023),
"Knowledge Updating in Real-World Estimation: Connecting Hindsight Bias and Seeding
Effects", JEP:General 152(11), 3167-3188, against any dataset in the Psych-301
unified schema (see schema.md).

Effects tested:
- exp1_hindsight_induction (exp0): Presenting actual population values after a
  judgment (concurrent/preceding feedback) makes the later recalled/revised estimate
  move toward the true value, i.e. order-of-magnitude error (OME=|log10(est/pop)|)
  DECREASES from OJ to ROJ on experimental (feedback) items. Paired t-test, d<0.
- exp1_transfer_learning (exp0): The seeded/feedback knowledge transfers to NEW items:
  OME DECREASES from OJ to OJnew in the feedback conditions (seeding effect), whereas
  the no-feedback control shows no improvement. Paired t-test per participant.
- exp2_hindsight (exp1): Hindsight bias on recall: OME DECREASES from OJScreen to
  ROJScreen, both under direct feedback (Feedback group) and under transfer/domain
  feedback on other items (Domain group). Paired t-test on matched OJ-ROJ items.
- exp2_transfer_learning (exp1): Transfer to new items: OME DECREASES from OJScreen to
  OJNScreen in the Feedback and Domain groups; Control shows no improvement. Paired
  t-test per participant.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0", "exp1"]

FEEDBACK_COND0 = ["concurrent_feedback", "preceding_feedback"]
FEEDBACK_COND1 = ["feedback", "domain"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD.
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _ome(df: pd.DataFrame) -> pd.Series:
    resp = pd.to_numeric(df["response"], errors="coerce")
    return (resp / df["population"]).apply(np.log10).abs()


def _paired(df: pd.DataFrame, mask_a: pd.Series, mask_b: pd.Series) -> tuple[float, float, float, float]:
    """Paired t-test of OME between two subsets sharing participant_id."""
    a = df[mask_a].copy()
    b = df[mask_b].copy()
    a["ome"] = _ome(a)
    b["ome"] = _ome(b)
    ma = a.groupby("participant_id")["ome"].mean()
    mb = b.groupby("participant_id")["ome"].mean()
    j = pd.concat([ma, mb], axis=1, keys=["a", "b"]).dropna()
    t, p = stats.ttest_rel(j["b"], j["a"])
    return float(j["a"].mean()), float(j["b"].mean()), float(t), float(p)


def check_exp1_hindsight_induction(data: dict[str, pd.DataFrame]) -> dict:
    """\"...the classical approach to induce hindsight bias indeed produces transfer
    learning\" — Gross et al. 2023, Abstract. Presenting feedback makes recall move
    toward the true value: OME (OJ->ROJ) declines in the feedback conditions."""
    df = data["exp0"]
    fb = df["condition"].isin(FEEDBACK_COND0) & (df["itemtype"] == 1)
    oj = fb & (df["phase"] == "oj")
    rj = fb & (df["phase"] == "roj")
    oj_m, rj_m, t, p = _paired(df, oj, rj)
    d = rj_m - oj_m
    reproduced = bool(d < 0 and p < 0.05)
    return {
        "effect_name": "exp1_hindsight_induction",
        "experiment": "exp0",
        "original_effect_size": -0.10,
        "effect_size": d,
        "reproduced": reproduced,
        "p": p,
        "t": t,
    }


def check_exp1_transfer_learning(data: dict[str, pd.DataFrame]) -> dict:
    """\"...hindsight bias is driven by adaptive learning processes... transfer
    learning\" — Gross et al. 2023, Abstract. Seeded feedback improves estimation on
    NEW items (OJ->OJnew) in the feedback conditions."""
    df = data["exp0"]
    fb = df["condition"].isin(FEEDBACK_COND0)
    oj = fb & (df["phase"] == "oj")
    nn = fb & (df["phase"] == "ojnew")
    oj_m, nn_m, t, p = _paired(df, oj, nn)
    d = nn_m - oj_m
    reproduced = bool(d < 0 and p < 0.05)
    return {
        "effect_name": "exp1_transfer_learning",
        "experiment": "exp0",
        "original_effect_size": -0.07,
        "effect_size": d,
        "reproduced": reproduced,
        "p": p,
        "t": t,
    }


def check_exp2_hindsight(data: dict[str, pd.DataFrame]) -> dict:
    """\"we provide evidence for the novel prediction that hindsight bias can be
    triggered via transfer learning\" — Gross et al. 2023, Abstract. Recall (ROJScreen)
    moves toward true values vs original judgment (OJScreen), both under direct
    (Feedback) and transfer/domain (Domain) feedback, on matched items."""
    df = data["exp1"].copy()
    df["ome"] = _ome(df)
    hj = df[df["phase"].isin(["ojscreen", "rojscreen"]) & df["condition"].isin(FEEDBACK_COND1)]
    pivot = hj.pivot_table(index=["participant_id", "idn"], columns="phase",
                           values="ome", aggfunc="mean").dropna()
    o, r = pivot["ojscreen"], pivot["rojscreen"]
    t, p = stats.ttest_rel(r, o)
    d = float((r - o).mean())
    reproduced = bool(d < 0 and p < 0.05)
    return {
        "effect_name": "exp2_hindsight",
        "experiment": "exp1",
        "original_effect_size": -0.06,
        "effect_size": d,
        "reproduced": reproduced,
        "p": p,
        "t": t,
    }


def check_exp2_transfer_learning(data: dict[str, pd.DataFrame]) -> dict:
    """\"...can be expected to lead to transfer learning and thus improve estimation
    for objects from a domain more generally\" — Gross et al. 2023, Abstract. New-item
    estimates (OJNScreen) improve relative to OJScreen in Feedback and Domain groups."""
    df = data["exp1"]
    fb = df["condition"].isin(FEEDBACK_COND1)
    oj = fb & (df["phase"] == "ojscreen")
    nn = fb & (df["phase"] == "ojnscreen")
    oj_m, nn_m, t, p = _paired(df, oj, nn)
    d = nn_m - oj_m
    reproduced = bool(d < 0 and p < 0.05)
    return {
        "effect_name": "exp2_transfer_learning",
        "experiment": "exp1",
        "original_effect_size": -0.10,
        "effect_size": d,
        "reproduced": reproduced,
        "p": p,
        "t": t,
    }


EFFECTS = [
    check_exp1_hindsight_induction,
    check_exp1_transfer_learning,
    check_exp2_hindsight,
    check_exp2_transfer_learning,
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
    print(f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  {'p':>8}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{r['p']:>8.4f}  {'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()
