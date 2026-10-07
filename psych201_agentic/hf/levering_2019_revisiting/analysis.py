# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Levering, Conaway, & Kurtz (2019),
"Revisiting the linear separability constraint: New implications for theories of
human category learning", Memory & Cognition 48:335-347, against any dataset in
the Psych-301 unified schema (see schema.md).

Effects tested:
- nls_advantage_training (exp0): mean classification accuracy over the 25
  training blocks is higher for the non-linearly separable (NLS) group than the
  linearly separable (LS) group; independent-samples t-test, expected NLS > LS.
- nls_advantage_test (exp0): mean classification accuracy on the six trained
  exemplars in the (no-feedback) test phase is higher for NLS than LS;
  independent-samples t-test, expected NLS > LS.
- nls_exception_items_harder_training (exp0): within NLS learners, accuracy on
  the two exception items (logical 100/101) is lower than on the other four
  trained items across training; paired t-test, expected exception < other.
- nls_prototype_items_easier_training (exp0): within NLS learners, accuracy on
  the two prototype items (logical 001/110) is higher than on the intermediate
  items (logical 011/010) across training; paired t-test, expected prototype >
  intermediate.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0"]

EXCEPTION_ITEMS = {"100", "101"}   # NLS exception items (logical 0/1 coding)
PROTOTYPE_ITEMS = {"001", "110"}   # NLS prototype items (logical 0/1 coding)
INTERMEDIATE_ITEMS = {"011", "010"}  # NLS intermediate items (logical 0/1 coding)


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD. Required columns in exp0: participant_id,
    condition, phase, trial, block, response, response_type, feature1, feature2,
    feature3, correct, trained.
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _logical_item(row: pd.Series) -> str:
    """Map the 1/2-valued logical features on a row to the paper's 0/1 digit string."""
    return (
        f"{int(row['feature1']) - 1}{int(row['feature2']) - 1}{int(row['feature3']) - 1}"
    )


def _cohens_d(a: np.ndarray, b: np.ndarray, paired: bool = False) -> float:
    if paired:
        return float(np.mean(a - b) / np.std(a - b, ddof=1))
    na, nb = len(a), len(b)
    sp = np.sqrt(((na - 1) * np.var(a, ddof=1) + (nb - 1) * np.var(b, ddof=1)) / (na + nb - 2))
    return float((np.mean(a) - np.mean(b)) / sp)


def check_nls_advantage_training(data: dict[str, pd.DataFrame]) -> dict:
    """'In contrast to the original findings, there was also a significant main
    effect of classification problem, F(1, 268) = 15.054, p < .001, eta2 = .053.
    Specifically, proportion correct for the NLS problem (M = .806, SD = .125) was
    significantly greater than for the LS problem (M = .745, SD = .134).' —
    Levering et al., 2020, p.339, Behavioral data: Aggregate learning."""
    df = data["exp0"]
    tr = df[(df["phase"] == "training")].dropna(subset=["correct"]).copy()
    acc = tr.groupby(["participant_id", "condition"])["correct"].mean().reset_index()
    ls = acc.loc[acc["condition"] == "ls", "correct"].to_numpy()
    nls = acc.loc[acc["condition"] == "nls", "correct"].to_numpy()
    t, p = stats.ttest_ind(nls, ls, equal_var=False)
    eta2 = t**2 / (t**2 + (len(ls) + len(nls) - 2))
    reproduced = bool(np.mean(nls) > np.mean(ls) and p < 0.05)
    return {
        "effect_name": "nls_advantage_training",
        "experiment": "exp0",
        "original_effect_size": 0.053,           # partial eta^2, F(1,268)=15.054
        "effect_size": float(eta2),
        "n_ls": int(len(ls)),
        "n_nls": int(len(nls)),
        "m_ls": float(np.mean(ls)),
        "m_nls": float(np.mean(nls)),
        "t": float(t),
        "p": float(p),
        "reproduced": reproduced,
    }


def check_nls_advantage_test(data: dict[str, pd.DataFrame]) -> dict:
    """'This difference was also observed at test, where performance of the NLS
    group (M = .923, SD = .149) was significantly higher than that of the LS group
    (M = .838, SD = .201), t(264) = 3.902, p < .001, d = .453.' — Levering et al.,
    2020, p.339, Behavioral data: Aggregate learning."""
    df = data["exp0"]
    te = df[(df["phase"] == "singletypicality") & (df["trained"] == 1)]
    te = te.dropna(subset=["correct"]).copy()
    acc = te.groupby(["participant_id", "condition"])["correct"].mean().reset_index()
    ls = acc.loc[acc["condition"] == "ls", "correct"].to_numpy()
    nls = acc.loc[acc["condition"] == "nls", "correct"].to_numpy()
    t, p = stats.ttest_ind(nls, ls, equal_var=False)
    d = _cohens_d(nls, ls)
    reproduced = bool(np.mean(nls) > np.mean(ls) and p < 0.05)
    return {
        "effect_name": "nls_advantage_test",
        "experiment": "exp0",
        "original_effect_size": 0.453,           # Cohen's d, t(264)=3.902
        "effect_size": d,
        "n_ls": int(len(ls)),
        "n_nls": int(len(nls)),
        "m_ls": float(np.mean(ls)),
        "m_nls": float(np.mean(nls)),
        "t": float(t),
        "p": float(p),
        "reproduced": reproduced,
    }


def check_nls_exception_items_harder_training(data: dict[str, pd.DataFrame]) -> dict:
    """'Consistent with previous research and these predictions, NLS exception
    items showed significantly worse performance (M = .755, SD = .159) than the
    other items (M = .832, SD = .128) during training, t(125) = 6.71, p < .001.' —
    Levering et al., 2020, p.339, Behavioral data: Representation of NLS
    categories."""
    df = data["exp0"]
    tr = df[(df["phase"] == "training") & (df["condition"] == "nls")]
    tr = tr.dropna(subset=["correct"]).copy()
    tr["log"] = tr.apply(_logical_item, axis=1)
    exc, other = [], []
    for _, g in tr.groupby("participant_id"):
        exc.append(g.loc[g["log"].isin(EXCEPTION_ITEMS), "correct"].mean())
        other.append(g.loc[~g["log"].isin(EXCEPTION_ITEMS), "correct"].mean())
    exc = np.asarray(exc)
    other = np.asarray(other)
    t, p = stats.ttest_rel(exc, other)
    d = _cohens_d(exc, other, paired=True)
    reproduced = bool(np.mean(exc) < np.mean(other) and p < 0.05)
    return {
        "effect_name": "nls_exception_items_harder_training",
        "experiment": "exp0",
        "original_effect_size": 6.71,            # paired t, t(125)=6.71
        "effect_size": d,
        "n": int(len(exc)),
        "m_exception": float(np.mean(exc)),
        "m_other": float(np.mean(other)),
        "t": float(t),
        "p": float(p),
        "reproduced": reproduced,
    }


def check_nls_prototype_items_easier_training(data: dict[str, pd.DataFrame]) -> dict:
    """'These items were classified more accurately than intermediate items during
    training, t(125) = 3.696, p < .001, and at test, t(125) = 1.999, p = .048.' —
    Levering et al., 2020, p.339, Behavioral data: Representation of NLS
    categories."""
    df = data["exp0"]
    tr = df[(df["phase"] == "training") & (df["condition"] == "nls")]
    tr = tr.dropna(subset=["correct"]).copy()
    tr["log"] = tr.apply(_logical_item, axis=1)
    proto, inter = [], []
    for _, g in tr.groupby("participant_id"):
        proto.append(g.loc[g["log"].isin(PROTOTYPE_ITEMS), "correct"].mean())
        inter.append(g.loc[g["log"].isin(INTERMEDIATE_ITEMS), "correct"].mean())
    proto = np.asarray(proto)
    inter = np.asarray(inter)
    t, p = stats.ttest_rel(proto, inter)
    d = _cohens_d(proto, inter, paired=True)
    reproduced = bool(np.mean(proto) > np.mean(inter) and p < 0.05)
    return {
        "effect_name": "nls_prototype_items_easier_training",
        "experiment": "exp0",
        "original_effect_size": 3.696,           # paired t, t(125)=3.696
        "effect_size": d,
        "n": int(len(proto)),
        "m_prototype": float(np.mean(proto)),
        "m_intermediate": float(np.mean(inter)),
        "t": float(t),
        "p": float(p),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_nls_advantage_training,
    check_nls_advantage_test,
    check_nls_exception_items_harder_training,
    check_nls_prototype_items_easier_training,
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