# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Witte et al. (2024) "Exploring the Unexplored"
against any dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- risky_condition_reduces_exploration (exp0, exp2): Studies 1 & 3 — the proportion of
  novel squares selected is lower in the risky (kraken-present) condition than in the safe
  condition. Tested via trial-by-trial logistic GEE (participant clusters). Expected: negative
  regression coefficient, p < .05 in both experiments.
- nervousness_increases_exploration (exp2): Study 3 — self-reported nervousness (state anxiety)
  during the task positively predicts the probability of selecting a novel option, controlling
  for risky vs safe condition. Tested via trial-by-trial logistic GEE. Expected: positive
  coefficient, p < .05.
- intervention_reduces_exploration (exp1): Study 2 — the metacognitive-therapy intervention
  reduced exploratory behaviour, as indexed by a negative interaction between timepoint
  (post vs pre) and condition (intervention vs control) predicting novel-option selection.
  Expected: negative interaction coefficient, p < .05.
"""
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.genmod.generalized_estimating_equations import GEE
from statsmodels.genmod.families import Binomial
from statsmodels.genmod.cov_struct import Exchangeable

EXPERIMENTS = ["exp0", "exp1", "exp2"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}."""
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _compute_novel(df: pd.DataFrame) -> pd.Series:
    df = df.sort_values(["participant_id", "task_id", "trial"])
    df["_cell"] = df["x"] * 11 + df["y"]
    novel = ~df.duplicated(subset=["participant_id", "task_id", "_cell"])
    novel = novel.where(df["x"].notna(), other=np.nan).astype(float)
    return novel.rename("_novel")


def check_risky_condition_reduces_exploration(data: dict[str, pd.DataFrame]) -> dict:
    """\"Overall, participants learned and performed well in both versions of the task ... the
    participants' proportion of novel squares selected was significantly reduced in the risky
    condition (β = −1.00, 95%CI: −1.06, −0.95 in Study 1 ... and β = −1.24, 95%CI: −1.52,
    −0.91 in Study 3)\" — Witte et al. (2024), p.4, Model-agnostic results."""
    eff_name = "risky_condition_reduces_exploration"
    reproduced = True
    coefs = []
    for e in ["exp0", "exp2"]:
        df = data[e].copy()
        d = df[df["valid"] == 1].dropna(subset=["x", "y"])
        d["_novel"] = _compute_novel(d)
        d["risky"] = (d["condition"] == "risky").astype(float)
        d = d.dropna(subset=["_novel", "risky"])
        mod = GEE.from_formula(
            "_novel ~ risky", groups=d["participant_id"], data=d,
            family=Binomial(), cov_struct=Exchangeable()
        )
        res = mod.fit(maxiter=60)
        c = res.params["risky"]
        p = res.pvalues["risky"]
        coefs.append(float(c))
        if not (c < 0 and p < 0.05):
            reproduced = False
    return {
        "effect_name": eff_name,
        "experiment": "exp0 (S1) & exp2 (S3)",
        "original_effect_size": -1.12,
        "effect_size": float(np.mean(coefs)),
        "reproduced": reproduced,
    }


def check_nervousness_increases_exploration(data: dict[str, pd.DataFrame]) -> dict:
    """\"... self-reported nervousness was significantly predicting the probability of selecting
    a novel option (β = 0.59, 95% HDI: 0.21,0.99)\" — Witte et al. (2024), p.4, State nervousness
    is still related to increased exploration in the absence of an intervention."""
    df = data["exp2"].copy()
    d = df[(df["valid"] == 1) & (df["task_id"] > 0)].dropna(subset=["x", "y", "nervous"])
    d["_novel"] = _compute_novel(d)
    d["risky"] = (d["condition"] == "risky").astype(float)
    nz_mean = d["nervous"].mean()
    nz_std = d["nervous"].std()
    d["nervous_z"] = (d["nervous"] - nz_mean) / nz_std
    d = d.dropna(subset=["_novel", "nervous_z", "risky"])
    mod = GEE.from_formula(
        "_novel ~ nervous_z + risky", groups=d["participant_id"], data=d,
        family=Binomial(), cov_struct=Exchangeable()
    )
    res = mod.fit(maxiter=60)
    c = float(res.params["nervous_z"])
    p = float(res.pvalues["nervous_z"])
    return {
        "effect_name": "nervousness_increases_exploration",
        "experiment": "exp2 (S3)",
        "original_effect_size": 0.59,
        "effect_size": c,
        "reproduced": c > 0 and p < 0.05,
    }


def check_intervention_reduces_exploration(data: dict[str, pd.DataFrame]) -> dict:
    """\"Participants in the intervention condition decreased their exploration behaviour
    following the intervention (β = -0.98, 95%CI: -1.92, -0.03)\" — Witte et al. (2024), p.4,
    Experimentally reducing worries reduces exploration behaviour."""
    df = data["exp1"].copy()
    d = df[(df["valid"] == 1) & (df["task_id"] > 0)].dropna(subset=["unique"])
    d["is_interv"] = (d["condition"] == "intervention").astype(float)
    d["is_post"] = (d["phase"] == "post_intervention").astype(float)
    d["interv_x_post"] = d["is_interv"] * d["is_post"]
    mod = GEE.from_formula(
        "unique ~ is_interv + is_post + interv_x_post",
        groups=d["participant_id"], data=d,
        family=Binomial(), cov_struct=Exchangeable()
    )
    res = mod.fit(maxiter=60)
    c = float(res.params["interv_x_post"])
    p = float(res.pvalues["interv_x_post"])
    return {
        "effect_name": "intervention_reduces_exploration",
        "experiment": "exp1 (S2)",
        "original_effect_size": -0.98,
        "effect_size": c,
        "reproduced": c < 0 and p < 0.05,
    }


EFFECTS = [
    check_risky_condition_reduces_exploration,
    check_nervousness_increases_exploration,
    check_intervention_reduces_exploration,
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
        print(f"{exp}:", sources.get(exp, "(default — local ./{exp}.csv)"))
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<14}  {'orig':>10}  {'this':>10}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<14}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()