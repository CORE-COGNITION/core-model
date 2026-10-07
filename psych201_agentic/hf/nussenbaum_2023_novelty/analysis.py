# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Nussenbaum, Martin et al. (2023,
eLife) "Novelty and uncertainty differentially drive exploration across
development" against any dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- novelty_seeking_choice (exp0): participants are biased to choose the more
  novel option; binomial GLM of choice on Δnovelty (+ controls/age), coefficient > 0.
- uncertainty_aversion_choice (exp0): participants avoid the more uncertain
  option; binomial GLM of choice on Δuncertainty, coefficient < 0.
- uncertainty_aversion_increases_with_age (exp0): age × Δuncertainty
  interaction coefficient < 0 (greater uncertainty aversion in older participants).
- novelty_seeking_stable_with_age (exp0): age × Δnovelty interaction not
  significant (novelty preference does not change across age).

Choice features are computed per option exactly as in the paper Methods
("Age-related change in exploration"): expected value = mean of the Beta
distribution over within-block wins/losses; uncertainty = its variance;
novelty = variance of a Beta(α = #prior exposures + 1, β = 1) distribution.
Only freely chosen, valid trials with RT >= 200 ms are analyzed.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

EXPERIMENTS = ["exp0"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD.
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _feature_df(df: pd.DataFrame) -> pd.DataFrame:
    """Free-choice exploration trials with RT >= 200 ms, plus choice features."""
    d = df[(df["phase"] == "exploration")
           & (df["valid"] == 1)
           & (df["rt"] >= 200)
           & (df["response"].notna())].copy()
    for i in (1, 2):
        wexp = f"exposureHistory_b_{i}"
        wwin = f"winHistory_b_{i}"
        wlos = f"lossHistory_b_{i}"
        if wexp in d.columns:
            e = d[wexp].astype(float)
            d[f"nov_{i}"] = (e + 1.0) / ((e + 2.0) ** 2 * (e + 3.0))
        else:
            d[f"nov_{i}"] = np.nan
        if wwin in d.columns and wlos in d.columns:
            a = d[wwin].astype(float) + 1.0
            b = d[wlos].astype(float) + 1.0
            d[f"ev_{i}"] = a / (a + b)
            d[f"u_{i}"] = (a * b) / ((a + b) ** 2 * (a + b + 1.0))
        else:
            d[f"ev_{i}"] = np.nan
            d[f"u_{i}"] = np.nan
    # response codes 0/1 = chose trialStimID_1 / trialStimID_2 (the transform's
    # coding). Code Y = "chose the first presented stimulus" so a POSITIVE
    # coefficient on a feature difference (stim_1 - stim_2) means participants
    # picked the option with the higher value of that feature, matching the
    # odds-ratio direction reported in the paper.
    d["chose_first"] = (d["response"] == 0).astype(int)
    d["dEV"] = d["ev_1"] - d["ev_2"]
    d["dU"] = d["u_1"] - d["u_2"]
    d["dN"] = d["nov_1"] - d["nov_2"]
    d = d.dropna(subset=["dEV", "dU", "dN"])
    return d


def _fit_model(d: pd.DataFrame):
    """Cluster-robust binomial GLM of choice on feature differences × age.

    Returns (params, pvalues) dicts with cluster-robust Wald inference.
    """
    for c in ["dEV", "dU", "dN", "age"]:
        m, s = d[c].mean(), d[c].std()
        d[c] = (d[c] - m) / s if s > 0 else d[c] - m
    formula = "chose_first ~ dEV + dU + dN + age + dEV:age + dU:age + dN:age"
    mod = smf.glm(formula, data=d, family=sm.families.Binomial())
    res = mod.fit(cov_type="cluster", cov_kwds={"groups": d["participant_id"]})
    return res.params, res.pvalues


def check_novelty_seeking_choice(data: dict[str, pd.DataFrame]) -> dict:
    """\"Participants also demonstrated a bias toward selecting more novel
    stimuli, OR = 1.34 [1.28, 1.41], x2(1) = 104.2, p < 0.001\" — Nussenbaum et
    al. 2023, p.4-5, Results ('Age-related change in exploration')."""
    params, pvals = _fit_model(_feature_df(data["exp0"]))
    beta = params["dN"]
    reproduced = bool(beta > 0 and pvals["dN"] < 0.05)
    return {
        "effect_name": "novelty_seeking_choice",
        "experiment": "exp0",
        "original_effect_size": float(np.log(1.34)),
        "effect_size": float(beta),
        "p": float(pvals["dN"]),
        "reproduced": reproduced,
    }


def check_uncertainty_aversion_choice(data: dict[str, pd.DataFrame]) -> dict:
    """\"...and a bias away from choosing options with greater uncertainty,
    OR = 0.89 [0.83, 0.95], x2(1) = 11.9, p < 0.001\" — Nussenbaum et al. 2023,
    p.4-5, Results ('Age-related change in exploration')."""
    params, pvals = _fit_model(_feature_df(data["exp0"]))
    beta = params["dU"]
    reproduced = bool(beta < 0 and pvals["dU"] < 0.05)
    return {
        "effect_name": "uncertainty_aversion_choice",
        "experiment": "exp0",
        "original_effect_size": float(np.log(0.89)),
        "effect_size": float(beta),
        "p": float(pvals["dU"]),
        "reproduced": reproduced,
    }


def check_uncertainty_aversion_increases_with_age(data: dict[str, pd.DataFrame]) -> dict:
    """\"...we observed a significant age x uncertainty interaction effect,
    OR = 0.89 [0.84, 0.95], x2(1) = 11.3, p < 0.001, indicating greater
    uncertainty aversion in older participants\" — Nussenbaum et al. 2023, p.5,
    Results ('Age-related change in exploration')."""
    params, pvals = _fit_model(_feature_df(data["exp0"]))
    beta = params["dU:age"]
    reproduced = bool(beta < 0 and pvals["dU:age"] < 0.05)
    return {
        "effect_name": "uncertainty_aversion_increases_with_age",
        "experiment": "exp0",
        "original_effect_size": float(np.log(0.89)),
        "effect_size": float(beta),
        "p": float(pvals["dU:age"]),
        "reproduced": reproduced,
    }


def check_novelty_seeking_stable_with_age(data: dict[str, pd.DataFrame]) -> dict:
    """\"...there was not a significant interaction between age and novelty,
    OR = 1.02 [0.98, 1.07], x2(1) = 0.96, p = 0.327\" — Nussenbaum et al. 2023,
    p.5, Results ('Age-related change in exploration'). This is a null claim
    (novelty preference stable across age), so it reproduces when the local
    age x novelty interaction is not significant."""
    params, pvals = _fit_model(_feature_df(data["exp0"]))
    beta = params["dN:age"]
    reproduced = bool(pvals["dN:age"] >= 0.05)
    return {
        "effect_name": "novelty_seeking_stable_with_age",
        "experiment": "exp0",
        "original_effect_size": float(np.log(1.02)),
        "effect_size": float(beta),
        "p": float(pvals["dN:age"]),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_novelty_seeking_choice,
    check_uncertainty_aversion_choice,
    check_uncertainty_aversion_increases_with_age,
    check_novelty_seeking_stable_with_age,
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