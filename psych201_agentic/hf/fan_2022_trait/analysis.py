# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Fan, Gershman & Phelps (2023), Trait
somatic anxiety is associated with reduced directed exploration and
underestimation of uncertainty (Nature Human Behaviour 7, 102-113) against any
dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- directed_exploration_reduced_somatic (exp0, exp1): higher trait somatic anxiety
  predicts a lower likelihood of choosing the option with greater posterior
  uncertainty (directed exploration); tested as a (Spearman) correlation between
  each subject's P(choose uncertain) and somatic-anxiety factor score. Expected
  direction: negative.
- underestimation_uncertainty_somatic (exp1): in the Study-2 reward-prediction
  task, higher trait somatic anxiety attenuates the positive relationship between
  normative and subjective total uncertainty (underestimation); tested as the
  interaction of somatic anxiety x normative total uncertainty (est_s1+est_s2) on
  subjective TU (= -(conf_a + conf_b)) in an OLS regression. Expected sign:
  negative interaction.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

EXPERIMENTS = ["exp0", "exp1"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame} for the experiments actually present.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD — cd into a checkout of the dataset repo (or pass
    --<exp> path on the CLI) before running.

    Required columns: participant_id, response, reward (both exp); exp0/exp1
    bandit: est_s1, est_s2; anxiety factor: Factor1_Somatic_Anxiety (fallback
    STICSAT_total_Somatic); exp1 prediction rows: conf_rating, est_s1, est_s2.
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _somatic_factor(df: pd.DataFrame) -> pd.Series:
    for col in ("Factor1_Somatic_Anxiety", "STICSAT_total_Somatic"):
        if col in df.columns and df[col].notna().any():
            return df[col].astype(float)
    raise KeyError("no somatic-anxiety column available")


def check_directed_exploration_reduced_somatic(data: dict[str, pd.DataFrame]) -> dict:
    """"We demonstrated that ... trait somatic anxiety ... was inversely correlated with
    directed exploration ... manifesting as a lesser likelihood for choosing the
    uncertain option." — Fan, Gershman & Phelps, 2023, Abstract."""
    rows = []
    for exp in EXPERIMENTS:
        if exp not in data:
            continue
        df = data[exp]
        band = df[df["reward"].notna()].copy()  # bandit choice rows only
        if not {"response", "est_s1", "est_s2"}.issubset(band.columns):
            continue
        band = band[band["est_s1"].notna() & band["est_s2"].notna()]
        band["most_unc"] = np.where(band["est_s1"] >= band["est_s2"], 1, 0)
        band["chose_unc"] = (band["response"] == band["most_unc"]).astype(int)
        som = _somatic_factor(band)
        g = band.assign(som=som).groupby("participant_id").agg(
            punc=("chose_unc", "mean"), som=("som", "first"))
        rows.append(g)
    g = pd.concat(rows, ignore_index=True).dropna()
    rho = stats.spearmanr(g["punc"], g["som"])
    reproduced = bool(rho.statistic < 0 and rho.pvalue < 0.05)
    return {
        "effect_name": "directed_exploration_reduced_somatic",
        "experiment": "exp0,exp1",
        "original_effect_size": -0.5,  # direction per abstract; no exact stat reported
        "effect_size": float(rho.statistic),
        "pvalue": float(rho.pvalue),
        "n_subjects": int(len(g)),
        "reproduced": reproduced,
    }


def check_underestimation_uncertainty_somatic(data: dict[str, pd.DataFrame]) -> dict:
    """Subjective TUt = w1*TUt + w2n*(TUt:Anx) ... a negative interaction between
    Somatic Anxiety and normative total uncertainty (B = -0.152 ± 0.039, t(12076)
    = -3.90, p < .001), indicating an underestimation of total uncertainty among
    trait somatic anxious individuals." — Fan, Gershman & Phelps, 2023, Suppl.
    Methods & Results (Supplementary Table 6)."""
    if "exp1" not in data:
        return {"effect_name": "underestimation_uncertainty_somatic", "experiment": "exp1",
                "original_effect_size": -0.152, "effect_size": np.nan,
                "reproduced": False}
    df = data["exp1"]
    pred = df[df["task_id"] == 30]
    conf = pred[pred["conf_rating"].notna()]
    if not {"conf_rating", "est_s1", "est_s2", "block", "pred_machine"}.issubset(conf.columns):
        return {"effect_name": "underestimation_uncertainty_somatic", "experiment": "exp1",
                "original_effect_size": -0.152, "effect_size": np.nan,
                "reproduced": False}
    key = conf["participant_id"].astype(str) + "_" + conf["block"].astype(str)
    p = conf.assign(key=key).pivot_table(index="key", columns="pred_machine",
                                         values="conf_rating").reset_index()
    p.columns = ["key", "cm0", "cm1"]
    p["SubjTU"] = -(p["cm0"] + p["cm1"])
    s = conf.assign(key=key).groupby("key").agg(
        nu1=("est_s1", "first"), nu2=("est_s2", "first"),
        som=("Factor1_Somatic_Anxiety", "first") if "Factor1_Somatic_Anxiety" in conf.columns
        else ("STICSAT_total_Somatic", "first")).reset_index()
    s["NTU"] = s["nu1"] + s["nu2"]
    j = p.merge(s, on="key").dropna(subset=["SubjTU", "NTU", "som"])
    m = sm.OLS.from_formula("SubjTU ~ NTU*som", data=j).fit()
    inter = float(m.params["NTU:som"])
    pval = float(m.pvalues["NTU:som"])
    reproduced = bool(inter < 0 and pval < 0.05)
    return {
        "effect_name": "underestimation_uncertainty_somatic",
        "experiment": "exp1",
        "original_effect_size": -0.152,
        "effect_size": inter,
        "pvalue": pval,
        "n_blocks": int(len(j)),
        "reproduced": reproduced,
    }


EFFECTS = [check_directed_exploration_reduced_somatic, check_underestimation_uncertainty_somatic]


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
        if exp in sources:
            print(f"{exp}: {sources[exp]}")
        else:
            print(f"{exp}: (default — local ./{exp}.csv)")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<8}  {'orig':>10}  {'this':>10}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<8}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()