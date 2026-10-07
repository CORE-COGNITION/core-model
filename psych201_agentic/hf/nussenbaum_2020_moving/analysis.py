# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Nussenbaum et al. (2020) against any dataset
in the Psych-301 unified schema (see schema.md).

Effects tested:
- reward_x_transition_x_age (exp0): Age-related increase in model-based learning.
  Mixed-effects logistic regression: stay ~ reward * transition * age.
  Expected: positive three-way interaction coefficient (reward:transition:age).
"""
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.genmod.families import Binomial
from statsmodels.genmod.cov_struct import Exchangeable

import json


EXPERIMENTS = ["exp0"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def prepare_two_step(df: pd.DataFrame) -> pd.DataFrame:
    df = df[(df["task_id"] == 0) & (df["phase"] == "test")].copy()

    stage1 = df[df["reward"].isna()].copy()
    stage2 = df[df["reward"].notna()].copy()

    merged = stage1[["participant_id", "block", "response", "age", "valid"]].rename(
        columns={"response": "choice_1", "valid": "valid_1"}
    ).merge(
        stage2[["participant_id", "block", "response", "reward", "transition", "valid"]].rename(
            columns={"response": "choice_2", "valid": "valid_2"}
        ),
        on=["participant_id", "block"],
    )

    merged = merged.sort_values(["participant_id", "block"]).reset_index(drop=True)

    merged = merged[merged["block"] >= 9].copy()
    merged = merged[(merged["valid_1"] == 1) & (merged["valid_2"] == 1)].copy()

    merged["transition_binary"] = (merged["transition"] == "common").astype(int)

    merged["prev_choice"] = merged.groupby("participant_id")["choice_1"].shift(1)
    merged["reward_prev"] = merged.groupby("participant_id")["reward"].shift(1)
    merged["transition_prev"] = merged.groupby("participant_id")["transition_binary"].shift(1)
    merged = merged.dropna(subset=["prev_choice", "reward_prev", "transition_prev"])
    merged["stay"] = (merged["choice_1"] == merged["prev_choice"]).astype(int)

    age_mean = merged["age"].mean()
    age_std = merged["age"].std()
    merged["age_z"] = (merged["age"] - age_mean) / age_std

    return merged


def check_reward_x_transition_x_age(data: dict[str, pd.DataFrame]) -> dict:
    """"we also observed a significant reward x transition x age interaction effect, indicating an age-related increase in model-based learning (ps < .002)" — Nussenbaum et al. 2020, p.7, Results."""
    two_step = prepare_two_step(data["exp0"])

    model = sm.GEE.from_formula(
        "stay ~ reward_prev * transition_prev * age_z",
        groups="participant_id",
        data=two_step,
        family=Binomial(),
        cov_struct=Exchangeable(),
    )
    result = model.fit(maxiter=200)

    coef = result.params["reward_prev:transition_prev:age_z"]
    pval = result.pvalues["reward_prev:transition_prev:age_z"]

    original_effect_size = 0.18
    reproduced = bool((coef > 0) and (pval < 0.05))

    return {
        "effect_name": "reward_x_transition_x_age",
        "experiment": "exp0",
        "original_effect_size": original_effect_size,
        "effect_size": float(coef),
        "p_value": float(pval),
        "reproduced": reproduced,
    }


EFFECTS = [check_reward_x_transition_x_age]


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
            print(f"{exp}: (default \u2014 local ./{exp}.csv)")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  {'p':>10}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{r['p_value']:>10.4f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")

    reproduced = [r["effect_name"] for r in results if r["reproduced"]]
    not_reproduced = [r["effect_name"] for r in results if not r["reproduced"]]
    status = "pass" if not_reproduced == [] else "fail"
    print(json.dumps({
        "status": status,
        "wrote_analysis": True,
        "reproduced": reproduced,
        "not_reproduced": not_reproduced,
        "notes": "",
    }))


if __name__ == "__main__":
    main()