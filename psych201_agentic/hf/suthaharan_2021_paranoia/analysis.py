# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Suthaharan et al. (2021), 'Paranoia and
belief updating during the COVID-19 crisis', Nat. Hum. Behav. 5, 1190-1202, against
any dataset in the Psych-301 unified schema (see schema.md).

Effects tested:
- paranoia_volatility_prior (exp0 pooled w/ exp1): Pearson correlation between RGPTS
  paranoia score and the HGF initial volatility prior mu03 (mean over blocks). The
  paper claims those with higher paranoia expect the task to be more unstable, so the
  correlation should be positive (higher paranoia -> higher mu03).
- paranoia_win_switch (exp0 pooled w/ exp1): Pearson correlation between RGPTS
  paranoia score and the win-switch rate (mean over blocks). The paper claims paranoid
  individuals switched more frequently / behaved more erratically, so the correlation
  should be positive.
- pandemic_paranoia_increase (exp1): RGPTS paranoia is higher in the lockdown and
  post-lockdown (reopening) periods than in the pre-lockdown baseline. The paper claims
  the onset of the pandemic increased paranoia that peaked during reopening.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0", "exp1"]

REF_COLS = [f"rgpts_ref_{i}" for i in range(1, 9)]
PER_COLS = [f"rgpts_per_{i}" for i in range(9, 19)]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides, loads
    ./{exp}.csv from CWD.

    Required columns per experiment:
      exp0: participant_id, trial, block, response, reward, plus rgpts_* and HGF mu03_*/wsr_block* covariates
      exp1: same shape.
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def participant_summary(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Collapse trial-level rows to one row per participant with the covariates
    needed for every effect below."""
    frames = []
    for exp in EXPERIMENTS:
        d = data[exp]
        g = d.groupby("participant_id").first()
        g = g.reset_index()
        g["exp"] = exp
        frames.append(g)
    df = pd.concat(frames, ignore_index=True)
    has_ref = all(c in df.columns for c in REF_COLS)
    has_per = all(c in df.columns for c in PER_COLS)
    df["paranoia"] = np.nan
    if has_ref:
        df["paranoia"] = df[REF_COLS].sum(axis=1, min_count=1)
        if has_per:
            df["paranoia"] = df[REF_COLS + PER_COLS].sum(axis=1, min_count=1)
    df["mu03"] = df[["mu03_1", "mu03_2"]].mean(axis=1)
    df["wsr"] = df[["wsr_block1", "wsr_block2"]].mean(axis=1)
    return df


def check_paranoia_volatility_prior(data: dict[str, pd.DataFrame]) -> dict:
    """\"In both tasks high paranoia subjects exhibit elevated priors for volatility
    (mu0_3; group: F (1, 198) = 8.566, p = 0.004)\" - Suthaharan et al. 2021, Fig. 2
    caption, p.1192."""
    df = participant_summary(data)
    sub = df.dropna(subset=["paranoia", "mu03"])
    r, p = stats.pearsonr(sub["paranoia"], sub["mu03"])
    reproduced = bool(r > 0 and p < 0.05)
    return {
        "effect_name": "paranoia_volatility_prior",
        "experiment": "exp0+exp1",
        "original_effect_size": 0.204,
        "effect_size": float(r),
        "p": float(p),
        "reproduced": reproduced,
    }


def check_paranoia_win_switch(data: dict[str, pd.DataFrame]) -> dict:
    """\"Participants with higher paranoia switched more frequently\" - Suthaharan et
    al. 2021, p.1191 (Introduction/Results)."""
    df = participant_summary(data)
    sub = df.dropna(subset=["paranoia", "wsr"])
    r, p = stats.pearsonr(sub["paranoia"], sub["wsr"])
    reproduced = bool(r > 0 and p < 0.05)
    return {
        "effect_name": "paranoia_win_switch",
        "experiment": "exp0+exp1",
        "original_effect_size": 0.35,
        "effect_size": float(r),
        "p": float(p),
        "reproduced": reproduced,
    }


def check_pandemic_paranoia_increase(data: dict[str, pd.DataFrame]) -> dict:
    """\"The onset of the pandemic was associated with increased self-reported paranoia
    from January 2020 through the lockdown ... peaking during reopening (Fig. 3a;
    F (2, 530) = 14.7, P < 0.001)\" - Suthaharan et al. 2021, Results, p.1193."""
    df = participant_summary(data)
    d1 = df[df["exp"] == "exp1"].dropna(subset=["paranoia"])
    pre = d1.loc[d1["period"] == "prelockdown", "paranoia"]
    post = d1.loc[d1["period"].isin(["lockdown", "postlockdown"]), "paranoia"]
    t, p = stats.ttest_ind(post, pre, equal_var=False)
    reproduced = bool(post.mean() > pre.mean() and p < 0.05)
    return {
        "effect_name": "pandemic_paranoia_increase",
        "experiment": "exp1",
        "original_effect_size": 0.053,
        "effect_size": float(post.mean() - pre.mean()),
        "p": float(p),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_paranoia_volatility_prior,
    check_paranoia_win_switch,
    check_pandemic_paranoia_increase,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. No printing - pure return value."""
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None,
                        help=f"CSV path for {exp}; defaults to ./{exp}.csv in CWD")
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS if getattr(args, exp)}
    for exp in EXPERIMENTS:
        if exp in sources:
            print(f"{exp}: {sources[exp]}")
        else:
            print(f"{exp}: (default - local ./{exp}.csv)")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<9}  {'orig':>10}  {'this':>10}  {'p':>10}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<9}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{r.get('p', 0):>10.4f}  {'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()
