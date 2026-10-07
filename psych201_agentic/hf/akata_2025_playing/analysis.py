# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Akata et al. (2025), "Playing repeated games
with large language models", Nature Human Behaviour, against any dataset in the
Psych-301 unified schema (see schema.md).

Effects tested:
- bos_scores_prompted (exp0): SCoT-prompted GPT-4 leads to higher average participant
  scores than base GPT-4 in the Battle of the Sexes (block==1). Between-condition
  comparison of each participant's mean BoS score; expected sign: prompted > base.
- bos_coordination_prompted (exp0): SCoT prompting increases successful coordination
  (both players picking the same option) in the Battle of the Sexes (block==1).
  Random-intercept logistic regression of BoS coordination rate (score!=0) on condition;
  expected sign: prompted > base.
- pd_joint_cooperation_prompted (exp0): SCoT prompting increases joint (mutual)
  cooperation in the Prisoner's Dilemma (block==0). Random-intercept logistic regression
  of PD joint-cooperation rate (score==5) on condition; expected sign: prompted > base.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM

EXPERIMENTS = ["exp0"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD — `cd` into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      exp0: participant_id, trial, response, reward (and: block, condition, coordination, phase)
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _game_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Keep the per-round game choices; the per-game opponent guesses are rows of
    their own (phase == "opponent_guess") with no reward."""
    return df[df["phase"] == "game"] if "phase" in df.columns else df


def _glmm_coef(df: pd.DataFrame, outcome: pd.Series) -> tuple[float, float, float]:
    """Fit a random-intercept logistic regression of `outcome` on condition
    (prompted vs base), mirroring the paper's lme4 glmer. Returns beta, z, p."""
    d = df.assign(out=outcome.astype(int))
    d["prom"] = d["condition"].map({"prompted": 1, "base": 0})
    design = BinomialBayesMixedGLM.from_formula(
        "out ~ prom", {"part": "0 + C(participant_id)"}, d
    )
    r = design.fit_vb()
    b = float(r.fe_mean[1])
    sd = float(r.fe_sd[1])
    z = b / sd
    p = 2 * stats.norm.cdf(-abs(z))
    return b, z, p


def check_bos_scores_prompted(data: dict[str, pd.DataFrame]) -> dict:
    """"While participants' average score was significantly higher for the SCoT-prompted
    condition compared with the condition without further prompting (that is, base) in
    the Battle of the Sexes (mixed-effects regression results: β = 0.74, t(193) = 3.49,
    P < 0.001...)" — Akata et al. 2025, p.1385, Human experiments."""
    df = _game_rows(data["exp0"])
    bos = df[df["block"] == 1]
    per = bos.groupby(["participant_id", "condition"])["reward"].mean().unstack()
    prom = per["prompted"].dropna().to_numpy()
    base = per["base"].dropna().to_numpy()
    t, p = stats.ttest_ind(prom, base, equal_var=False)
    effect_size = float(prom.mean() - base.mean())
    return {
        "effect_name": "bos_scores_prompted",
        "experiment": "exp0",
        "original_effect_size": 0.74,
        "effect_size": effect_size,
        "t": float(t),
        "p": float(p),
        "reproduced": bool(effect_size > 0 and p < 0.05),
    }


def check_bos_coordination_prompted(data: dict[str, pd.DataFrame]) -> dict:
    """"SCoT prompting increased successful coordination (that is, both players picking
    the same option) in the Battle of the Sexes (β = 0.33, z = 3.59, P < 0.001...)"
    — Akata et al. 2025, p.1385, Human experiments."""
    df = _game_rows(data["exp0"])
    bos = df[df["block"] == 1].copy()
    outcome = bos["reward"] != 0  # successful coordination in BoS: same option (score!=0)
    b, z, p = _glmm_coef(bos, outcome)
    effect_size = b
    return {
        "effect_name": "bos_coordination_prompted",
        "experiment": "exp0",
        "original_effect_size": 0.33,
        "effect_size": float(effect_size),
        "z": float(z),
        "p": float(p),
        "reproduced": bool(effect_size > 0 and p < 0.05),
    }


def check_pd_joint_cooperation_prompted(data: dict[str, pd.DataFrame]) -> dict:
    """"it also slightly increased joint cooperation (that is, both players cooperating)
    in the Prisoner's Dilemma (β = 0.24, z = 2.54, P = 0.01...)" — Akata et al. 2025,
    p.1386, Human experiments."""
    df = _game_rows(data["exp0"])
    pdg = df[df["block"] == 0].copy()
    outcome = pdg["reward"] == 5  # joint cooperation in PD (see paper's R script)
    b, z, p = _glmm_coef(pdg, outcome)
    effect_size = b
    return {
        "effect_name": "pd_joint_cooperation_prompted",
        "experiment": "exp0",
        "original_effect_size": 0.24,
        "effect_size": float(effect_size),
        "z": float(z),
        "p": float(p),
        "reproduced": bool(effect_size > 0 and p < 0.05),
    }


EFFECTS = [
    check_bos_scores_prompted,
    check_bos_coordination_prompted,
    check_pd_joint_cooperation_prompted,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. No printing — pure return value
    so downstream simulators / model evaluators can call this programmatically."""
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
              f"{r['p']:>8.3f}  {'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()
