# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Haridi, Schulz, & Thalmann (2025)
"Context-size and set size effects: The relevance of specific cues when
searching long-term memory" against any dataset in the Psych-301 unified schema.

Effects tested:
- set_size_rt_exp1 (exp0): RT increases with set size (ListLength) for correct recall responses; linear mixed model with log(RT), positive slope expected.
- similarity_rt_exp1 (exp0): RT decreases with cue-target semantic similarity (W2VWordPairsSim); per-participant Spearman correlation, negative mean rho expected.
- semantic_context_rt_exp3 (exp2): RT increases with semantic context size (ContextSize) for correct responses; linear mixed model with log(RT), positive slope expected.
- semantic_context_accuracy_exp3 (exp2): Accuracy decreases with semantic context size (ContextSize); per-participant Spearman correlation, negative mean rho expected.
"""
from __future__ import annotations

import argparse
import json
import warnings

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.regression.mixed_linear_model import MixedLM

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

EXPERIMENTS = ["exp0", "exp1", "exp2"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv"), low_memory=False) for exp in EXPERIMENTS}


def _zscore(s: pd.Series) -> np.ndarray:
    return (s - s.mean()) / s.std()


def _mixedlm_rt(data: pd.DataFrame, x_var: str) -> dict:
    d = data.copy()
    d["log_rt"] = np.log(d["rt"].values)
    d["x_z"] = _zscore(d[x_var].values)
    counts = d.groupby("participant_id").size()
    valid = counts[counts >= 2].index
    d = d[d["participant_id"].isin(valid)].copy()
    try:
        model = MixedLM.from_formula("log_rt ~ x_z", groups=d["participant_id"], data=d)
        result = model.fit(reml=True, maxiter=200)
        coef = result.params["x_z"]
        pval = result.pvalues["x_z"]
        return {"coef": float(coef), "pval": float(pval), "n": len(d)}
    except Exception as e:
        return {"coef": np.nan, "pval": np.nan, "error": str(e), "n": len(d)}


def check_set_size_rt_exp1(data: dict[str, pd.DataFrame]) -> dict:
    "\"As hypothesized, RTs increased with set size (β̂ = 0.09, 95% HDI = [0.05, 0.13], BF10 > 100)\" — Haridi et al., p.12, Results Experiment 1."
    df = data["exp0"]
    mask = (
        (df["valid"] == 1) & (df["phase"] == "cuepresentation")
        & (df["correct"] == 1) & (df["rt"] < 20000)
        & (df["ListLength"].notna())
    )
    sub = df[mask].copy()
    res = _mixedlm_rt(sub, "ListLength")
    reproduced = bool(res.get("coef", np.nan) > 0 and res.get("pval", 1) < 0.05)
    return {
        "effect_name": "set_size_rt_exp1", "experiment": "exp0",
        "original_effect_size": 0.09, "effect_size": res.get("coef", np.nan),
        "p_value": res.get("pval", np.nan), "reproduced": reproduced,
        "n_trials": res.get("n", 0),
    }


def check_similarity_rt_exp1(data: dict[str, pd.DataFrame]) -> dict:
    "\"Increased similarity between the cue and the target resulted in faster RTs (β̂ = −0.06, 95% HDI = [−0.08, −0.04], BF10 > 100)\" — Haridi et al., p.12, Results Experiment 1."
    df = data["exp0"]
    mask = (
        (df["valid"] == 1) & (df["phase"] == "cuepresentation")
        & (df["correct"] == 1) & (df["rt"] < 20000)
        & (df["W2VWordPairsSim"].notna())
    )
    sub = df[mask].copy()
    rhos = []
    for pid, grp in sub.groupby("participant_id"):
        if len(grp) < 3:
            continue
        r, _ = stats.spearmanr(grp["W2VWordPairsSim"], grp["rt"])
        rhos.append(r)
    rhos = np.array(rhos)
    if len(rhos) < 10:
        return {"effect_name": "similarity_rt_exp1", "experiment": "exp0",
                "original_effect_size": -0.06, "effect_size": np.nan,
                "p_value": np.nan, "reproduced": False, "n_participants": 0}
    t_stat, pval = stats.ttest_1samp(rhos, 0)
    mean_rho = float(rhos.mean())
    reproduced = bool(mean_rho < 0 and pval < 0.05)
    return {
        "effect_name": "similarity_rt_exp1", "experiment": "exp0",
        "original_effect_size": -0.06, "effect_size": mean_rho,
        "p_value": float(pval), "reproduced": reproduced,
        "n_participants": len(rhos),
    }


def check_semantic_context_rt_exp3(data: dict[str, pd.DataFrame]) -> dict:
    "\"RTs for correct responses took longer the more word-pairs were associated with a context cue (β̂ = 0.03, 95% HDI = [0.01, 0.05], BF10 = 1.22)\" — Haridi et al., p.17, Results Experiment 3."
    df = data["exp2"]
    mask = (
        (df["valid"] == 1) & (df["phase"] == "cuepresentation")
        & (df["correct"] == 1) & (df["rt"] < 20)
        & (df["ContextSize"].notna())
    )
    sub = df[mask].copy()
    res = _mixedlm_rt(sub, "ContextSize")
    reproduced = bool(res.get("coef", np.nan) > 0 and res.get("pval", 1) < 0.05)
    return {
        "effect_name": "semantic_context_rt_exp3", "experiment": "exp2",
        "original_effect_size": 0.03, "effect_size": res.get("coef", np.nan),
        "p_value": res.get("pval", np.nan), "reproduced": reproduced,
        "n_trials": res.get("n", 0),
    }


def check_semantic_context_accuracy_exp3(data: dict[str, pd.DataFrame]) -> dict:
    "\"Larger contexts were associated with a lower accuracy (β̂ = −0.27, 95% HDI = [−0.35, −0.19], BF10 > 100)\" — Haridi et al., p.17, Results Experiment 3."
    df = data["exp2"]
    mask = (
        (df["valid"] == 1) & (df["phase"] == "cuepresentation")
        & (df["correct"].notna()) & (df["ContextSize"].notna())
    )
    sub = df[mask].copy()
    rhos = []
    for pid, grp in sub.groupby("participant_id"):
        if len(grp) < 5:
            continue
        if grp["correct"].nunique() < 2:
            continue
        r, _ = stats.spearmanr(grp["ContextSize"], grp["correct"])
        rhos.append(r)
    rhos = np.array(rhos)
    if len(rhos) < 10:
        return {"effect_name": "semantic_context_accuracy_exp3", "experiment": "exp2",
                "original_effect_size": -0.27, "effect_size": np.nan,
                "p_value": np.nan, "reproduced": False, "n_participants": 0}
    t_stat, pval = stats.ttest_1samp(rhos, 0)
    mean_rho = float(rhos.mean())
    reproduced = bool(mean_rho < 0 and pval < 0.05)
    return {
        "effect_name": "semantic_context_accuracy_exp3", "experiment": "exp2",
        "original_effect_size": -0.27, "effect_size": mean_rho,
        "p_value": float(pval), "reproduced": reproduced,
        "n_participants": len(rhos),
    }


EFFECTS = [
    check_set_size_rt_exp1,
    check_similarity_rt_exp1,
    check_semantic_context_rt_exp3,
    check_semantic_context_accuracy_exp3,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None, help=f"CSV path for {exp}")
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS if getattr(args, exp)}
    for exp in EXPERIMENTS:
        src = sources.get(exp, "(default)")
        print(f"{exp}: {src}")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    hdr = f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  {'p':>8}  reproduced"
    print(hdr)
    reproduced_list = []
    not_reproduced_list = []
    for r in results:
        flag = "YES" if r["reproduced"] else "NO"
        p_str = f"{r['p_value']:.4f}" if "p_value" in r and not np.isnan(r["p_value"]) else "NA"
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{p_str:>8}  {flag}")
        if r["reproduced"]:
            reproduced_list.append(r["effect_name"])
        else:
            not_reproduced_list.append(r["effect_name"])
    status = "pass" if len(not_reproduced_list) == 0 else "fail"
    print()
    print(json.dumps({
        "status": status,
        "wrote_analysis": True,
        "reproduced": reproduced_list,
        "not_reproduced": not_reproduced_list,
        "notes": "" if status == "pass" else f"Failed: {', '.join(not_reproduced_list)}",
    }))


if __name__ == "__main__":
    main()