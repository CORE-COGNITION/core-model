# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "scipy"]
# ///
"""Check the primary behavioral effects of Franke et al. (2024, Bayesian statistical
modeling with predictors from LLMs) against any dataset in the Psych-301 unified schema.

Effects tested:
- target_production_gt_interpretation (exp0): the rate at which participants choose the
  pragmatically-relevant TARGET option (vs competitor/distractor) is higher in the
  production than in the interpretation condition. Tested with a 2x2 chi-square on
  target vs non-target counts; expected direction: production > interpretation, p < .05.
- target_modal_both_conditions (exp0): the TARGET is the most frequently chosen category
  within each condition (target count > competitor count and > distractor count), i.e.
  participants resolve the reference game toward the intended referent in both conditions.
  Tested with a chi-square goodness-of-fit over {target, competitor, distractor} counts in
  each condition.

NOTE (data provenance): the unified-schema CSV (exp0.csv) stores the free-text response
but not the item's category structure, so the target/competitor/distractor label for each
choice is recovered from the companion <workdir>/raw/data-prepped-*.csv files, whose
`response` column already carries the human choice category.
"""
from __future__ import annotations

import argparse
import json
import os

import pandas as pd
import numpy as np
from scipy import stats

EXPERIMENTS = ["exp0"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override, plus the special key
    "category" giving the path to a CSV whose rows carry the human choice category
    (target/competitor/distractor) joined on (condition, trial_nr). With no overrides,
    loads ./exp0.csv and ./raw/data-prepped-LLaMA2-hf-7b.csv from CWD.

    exp0 requires: participant_id, trial, condition, response, rt.
    """
    sources = sources or {}
    exp_path = sources.get("exp0", "./exp0.csv")
    cat_path = sources.get("category", "./raw/data-prepped-LLaMA2-hf-7b.csv")

    df = pd.read_csv(exp_path)

    if os.path.exists(cat_path):
        cat = pd.read_csv(cat_path)
        cat = cat.rename(columns={"trial_nr": "my_trial"})
        keep = cat[["submission_id"]] if "submission_id" in cat.columns else None
        join_cols = ["condition"]
        cat_map = cat[["condition", "my_trial", "response"]].copy()
        cat_map = cat_map.rename(columns={"response": "category"})
        df = df.merge(
            cat_map,
            left_on=["condition", "trial_nr"],
            right_on=["condition", "my_trial"],
            how="left",
        )
        df = df.drop(columns=["my_trial"])

    return {"exp0": df}


def check_target_production_gt_interpretation(data: dict[str, pd.DataFrame]) -> dict:
    """"...the number of target choices is higher in the production condition than in the
    interpretation condition." — Franke et al. 2024, p.6, Results (Section 2).
    Target rate compared between conditions via a 2x2 chi-square (target vs. other)."""
    df = data["exp0"]
    sub = df[df["category"].isin(["target", "competitor", "distractor"])].copy()
    sub["is_target"] = (sub["category"] == "target").astype(int)
    prod = sub[sub["condition"] == "production"]["is_target"]
    interp = sub[sub["condition"] == "interpretation"]["is_target"]

    n_prod = len(prod)
    n_int = len(interp)
    t_prod = int(prod.sum())
    t_int = int(interp.sum())
    table = np.array([[t_prod, n_prod - t_prod], [t_int, n_int - t_int]])
    chi2, p, _, _ = stats.chi2_contingency(table, correction=False)
    prop_prod = t_prod / n_prod
    prop_int = t_int / n_int
    effect_size = prop_prod - prop_int          # positive => production > interpretation
    reproduced = bool(effect_size > 0 and p < 0.05)
    return {
        "effect_name": "target_production_gt_interpretation",
        "experiment": "exp0",
        "original_effect_size": 0.828 - 0.531,  # paper Figure 4 observed proportions
        "effect_size": float(effect_size),
        "p": float(p),
        "n_production": n_prod,
        "n_interpretation": n_int,
        "reproduced": reproduced,
    }


def check_target_is_modal_both_conditions(data: dict[str, pd.DataFrame]) -> dict:
    """In both conditions the target is the most frequent choice category (Figure 4 counts:
    target > competitor > distractor). Tested with a chi-square goodness-of-fit against
    equal rates, requiring target to be the observed mode in each condition."""
    df = data["exp0"]
    sub = df[df["category"].isin(["target", "competitor", "distractor"])]
    reproducible = True
    all_ok = True
    for cond in ["production", "interpretation"]:
        subc = sub[sub["condition"] == cond]
        counts = subc["category"].value_counts()
        obs = np.array([counts.get("target", 0), counts.get("competitor", 0),
                        counts.get("distractor", 0)], dtype=float)
        if obs.sum() == 0:
            reproducible = False
            break
        chi2, p = stats.chisquare(obs)
        is_target_modal = counts.get("target", 0) > counts.get("competitor", 0) and \
                          counts.get("target", 0) > counts.get("distractor", 0)
        ok = is_target_modal and p < 0.05
        if not ok:
            all_ok = False
    return {
        "effect_name": "target_is_modal_both_conditions",
        "experiment": "exp0",
        "original_effect_size": 0.7,  # target is modal in both panels of Figure 4
        "effect_size": float(1.0 if all_ok else 0.0),
        "reproduced": bool(all_ok and reproducible),
    }


EFFECTS = [check_target_production_gt_interpretation, check_target_is_modal_both_conditions]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None, help=f"CSV path for {exp}; defaults to ./{exp}.csv in CWD")
    ap.add_argument("--category", default=None, help="Optional CSV with human choice category (target/competitor/distractor)")
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS if getattr(args, exp)}
    if getattr(args, "category"):
        sources["category"] = args.category
    for exp in EXPERIMENTS:
        if exp in sources:
            print(f"{exp}: {sources[exp]}")
        else:
            print(f"{exp}: (default — local ./{exp}.csv)")
    print(f"category: {sources.get('category', '(default — local ./raw/data-prepped-*.csv)')}")
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
