# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Hunter, "Excessive deliberation in social
anxiety" against any dataset in the Psych-301 unified schema (see schema.md).

The paper's headline finding is that self-reported social anxiety (LSAS) predicts
increased model-based ("counterfactual") evaluation in a socially framed RL task (the
Patent Race game), and that this is specific to *upward* counterfactual updating
(updating toward moves that would have done better), not downward counterfactual
updating. Model parameters (EWA delta/delta+) are not stored in the CSVs, so we
approximate each subject's upward (delta+) and downward (delta-) counterfactual
learning weight by a per-subject maximum-likelihood fit of a valenced EWA learning
model (inverse temperature, learning rate, delta+, delta-) to the trial-level choices,
and then regress these fitted weights on the z-scored LSAS covariate (controlling for
IQ via Ravens), as in the paper.

Effects tested:
- upward_counterfactual_social_anxiety (exp0, exp1): regression of per-subject delta+
  (upward counterfactual updating weight) on z-scored LSAS, controlling for Ravens —
  expected POSITIVE and significant (p < .05) in each experiment.
- downward_counterfactual_social_anxiety_null (exp0, exp1): regression of per-subject
  delta- (downward counterfactual updating weight) on z-scored LSAS, controlling for
  Ravens — expected NO significant effect (p > .05) in each experiment (specificity).
"""
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize

EXPERIMENTS = ["exp0", "exp1"]

# Payoff matrix M[subject_move s1 (0..4)][opponent_move s2 (0..5)] from the paper.
PAYOFF = np.array(
    [
        [4, 4, 4, 4, 4, 4],
        [13, 3, 3, 3, 3, 3],
        [12, 12, 2, 2, 2, 2],
        [11, 11, 11, 1, 1, 1],
        [10, 10, 10, 10, 0, 0],
    ],
    dtype=float,
)

_FIT_CACHE: dict = {}


def _valenced_nll(par, a, s2, r, cf, up, dn):
    """Negative log-likelihood of a valenced EWA model (delta+, delta-)."""
    beta, phi, dplus, dminus = par
    beta = max(beta, 1e-8)
    phi = np.clip(phi, 0, 1)
    Q = np.zeros(5)
    ll = 0.0
    for t in range(len(a)):
        v = Q * beta
        v -= v.max()
        p = np.exp(v)
        p /= p.sum()
        ll += np.log(p[a[t]])
        r_t = r[t]
        Q[a[t]] += phi * (r_t - Q[a[t]])
        Q += phi * (dplus * up[t] + dminus * dn[t]) * (cf[t] - Q)
    return -ll


def _fit_subject(a, s2, r):
    """Fit (beta, phi, delta+, delta-) per subject; return (delta+, delta-)."""
    cf = PAYOFF[:, s2].T.copy()
    up = (cf > r[:, None]).astype(float)
    dn = (cf < r[:, None]).astype(float)
    bounds = [(0.01, 20), (0, 1), (0, 1), (0, 1)]
    best = None
    best_val = 1e18
    for start in [np.array([1.0, 0.5, 0.5, 0.4])]:
        res = minimize(
            lambda pr: _valenced_nll(pr, a, s2, r, cf, up, dn),
            start,
            method="L-BFGS-B",
            bounds=bounds,
        )
        if res.fun < best_val:
            best_val = res.fun
            best = res
    return best.x[2], best.x[3]


def _fitted_params(df: pd.DataFrame) -> pd.DataFrame:
    """Per-subject (lsasZ, ravens, delta+, delta-) via cached valenced-EWA fits."""
    key = id(df)
    if key in _FIT_CACHE:
        return _FIT_CACHE[key]
    rows = []
    for _, g in df.groupby("participant_id"):
        a = (g["s1"].values - 1).astype(int)
        s2 = (g["s2"].values - 1).astype(int)
        r = g["reward"].values.astype(float)
        dp, dm = _fit_subject(a, s2, r)
        rows.append((g["lsasZ"].iloc[0], g["ravens"].iloc[0], dp, dm))
    out = pd.DataFrame(rows, columns=["lsas", "ravens", "dp", "dm"])
    _FIT_CACHE[key] = out
    return out


def _lsas_beta(df: pd.DataFrame, col: str):
    """Standardized beta of LSAS->col controlling for Ravens, plus p-value."""
    d = _fitted_params(df)
    y = d[col].values
    y = (y - y.mean()) / (y.std() + 1e-12)
    X = np.column_stack([np.ones(len(d)), d["ravens"].values, d["lsas"].values])
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    resid = y - X @ beta
    resid_l = d["lsas"].values - (
        X[:, :2] @ np.linalg.lstsq(X[:, :2], d["lsas"].values, rcond=None)[0]
    )
    r, p = stats.pearsonr(resid_l, resid + beta[2] * resid_l)
    return beta[2], p


def check_upward_counterfactual_social_anxiety(
    data: dict[str, pd.DataFrame],
) -> dict:
    """\"Indeed, social anxiety predicted a robust increase in upwards counterfactual
    updating, indexed by delta+ (p<0.0001), but had no significant relationship with
    delta-\" — Hunter, p.?? Results."""
    betas, ps = [], []
    for exp in EXPERIMENTS:
        b, p = _lsas_beta(data[exp], "dp")
        betas.append(b)
        ps.append(p)
    reproduced = all(b > 0 and p < 0.05 for b, p in zip(betas, ps))
    return {
        "effect_name": "upward_counterfactual_social_anxiety",
        "experiment": "exp0+exp1",
        "original_effect_size": 0.13,  # paper: delta~LSAS t=2.59/2.507, delta+ p<0.0001
        "effect_size": float(np.mean(betas)),
        "p_values": [round(p, 4) for p in ps],
        "reproduced": bool(reproduced),
    }


def check_downward_counterfactual_social_anxiety_null(
    data: dict[str, pd.DataFrame],
) -> dict:
    """\"...but had no significant relationship with delta-\" — Hunter, p.?? Results.
    Specificity: social anxiety increases upward but not downward counterfactual
    updating."""
    betas, ps = [], []
    for exp in EXPERIMENTS:
        b, p = _lsas_beta(data[exp], "dm")
        betas.append(b)
        ps.append(p)
    reproduced = all(p > 0.05 for p in ps)
    return {
        "effect_name": "downward_counterfactual_social_anxiety_null",
        "experiment": "exp0+exp1",
        "original_effect_size": 0.0,
        "effect_size": float(np.mean(betas)),
        "p_values": [round(p, 4) for p in ps],
        "reproduced": bool(reproduced),
    }


EFFECTS = [
    check_upward_counterfactual_social_anxiety,
    check_downward_counterfactual_social_anxiety_null,
]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}."""
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None)
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS if getattr(args, exp)}
    for exp in EXPERIMENTS:
        print(f"{exp}: {sources[exp] if exp in sources else '(default — local ./{exp}.csv)'}")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<12}  {'orig':>10}  {'this':>10}  reproduced")
    for r in results:
        pv = ",".join(str(p) for p in r.get("p_values", []))
        print(
            f"{r['effect_name']:<{w}}  {r['experiment']:<12}  "
            f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
            f"{'YES' if r['reproduced'] else 'NO'}  (p={pv})"
        )


if __name__ == "__main__":
    main()
