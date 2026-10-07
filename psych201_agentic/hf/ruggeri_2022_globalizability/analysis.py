# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Ruggeri et al. (2022), "The globalizability
of temporal discounting" (Nat. Hum. Behav.), against any dataset in the Psych-301
unified schema (see schema.md).

Effects tested:
- sign_effect (exp0): the sign effect / gain-loss asymmetry — gains are discounted more
  than losses. For gains, discounting = choosing the immediate "right now" option; for
  losses, discounting = choosing to delay the payment ("in 12 months"). Test: paired
  Wilcoxon comparing each participant's mean gain-discounting vs loss-discounting rate.
  Expected: gain discounting > loss discounting (positive), p < .05.
- absolute_magnitude (exp0): increased preference for delayed gains when magnitudes are
  substantially larger. Discounting (choosing immediate) should be lower for the large
  gain block (block 2) than the small gain block (block 0). Test: paired Wilcoxon of
  per-participant immediate-gain rates, small vs large. Expected: small > large, p < .05.
- assets_discounting (exp0): greater individual financial resources (self-reported assets,
  Q26_3) are associated with lower temporal discounting. Test: Spearman correlation between
  assets and per-participant mean discounting rate. Expected: negative, p < .05.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. Reads ./{exp}.csv from CWD.
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _analyzable(df: pd.DataFrame) -> pd.DataFrame:
    """Restrict to the paper's analyzed sample: participants who passed the attention
    check. The transform retains all rows including attention-check failures; the paper
    excluded them. Apply the same per-participant filter."""
    sub = df.copy()
    sub["_pass"] = (
        sub["Attention check"].fillna("").astype(str).str.strip().str.upper() == "PASS"
    )
    ok = sub.groupby("participant_id")["_pass"].transform("all")
    return sub[ok]


def _discounting_rates(df: pd.DataFrame) -> pd.DataFrame:
    """Per-participant mean discounting rate for gain items (choose immediate) and loss
    items (choose delayed payment). Decodes from the verbatim choice text."""
    sub = df.copy()
    sub["_is_gain"] = sub["block"].isin([0, 2])
    sub["_is_loss"] = sub["block"] == 1
    sub["_imm"] = sub["response"].astype(str).str.contains("right now", regex=False)
    sub["_delayed"] = sub["response"].astype(str).str.contains("in 12 months", regex=False)
    gain = sub[sub["_is_gain"]].groupby("participant_id")["_imm"].mean().rename("gain_disc")
    loss = sub[sub["_is_loss"]].groupby("participant_id")["_delayed"].mean().rename("loss_disc")
    return pd.concat([gain, loss], axis=1)


def check_sign_effect(data: dict[str, pd.DataFrame]) -> dict:
    """\"Gain–loss asymmetry: Gains are discounted more than losses, though differences
    (real and relative) are constant\" — Ruggeri et al. 2022, p.1387, Results/Methods."""
    df = _analyzable(data["exp0"])
    rates = _discounting_rates(df).dropna()
    if len(rates) < 20:
        return {"effect_name": "sign_effect", "experiment": "exp0",
                "original_effect_size": 0.4, "effect_size": np.nan, "reproduced": False}
    w = stats.wilcoxon(rates["gain_disc"], rates["loss_disc"])
    diff = float(rates["gain_disc"].mean() - rates["loss_disc"].mean())
    reproduced = bool(diff > 0 and w.pvalue < 0.05)
    return {
        "effect_name": "sign_effect",
        "experiment": "exp0",
        "original_effect_size": 0.401,
        "effect_size": diff,
        "p_value": float(w.pvalue),
        "reproduced": reproduced,
    }


def check_absolute_magnitude(data: dict[str, pd.DataFrame]) -> dict:
    """\"Absolute magnitude: Increased preference for delayed gains when values become
    substantially larger, even when relative differences are constant\" — Ruggeri et al.
    2022, p.1387, Methods."""
    df = _analyzable(data["exp0"])
    sub = df[df["block"].isin([0, 2])].copy()
    sub["_imm"] = sub["response"].astype(str).str.contains("right now", regex=False)
    small = sub[sub["block"] == 0].groupby("participant_id")["_imm"].mean().rename("small")
    large = sub[sub["block"] == 2].groupby("participant_id")["_imm"].mean().rename("large")
    m = pd.concat([small, large], axis=1).dropna()
    if len(m) < 20:
        return {"effect_name": "absolute_magnitude", "experiment": "exp0",
                "original_effect_size": 0.138, "effect_size": np.nan, "reproduced": False}
    w = stats.wilcoxon(m["small"], m["large"])
    diff = float(m["small"].mean() - m["large"].mean())
    reproduced = bool(diff > 0 and w.pvalue < 0.05)
    return {
        "effect_name": "absolute_magnitude",
        "experiment": "exp0",
        "original_effect_size": 0.138,
        "effect_size": diff,
        "p_value": float(w.pvalue),
        "reproduced": reproduced,
    }


def check_assets_discounting(data: dict[str, pd.DataFrame]) -> dict:
    """\"Temporal discounting scores generally decreased as wealth increased\" — Ruggeri
    et al. 2022, p.1392, Results (Assets and debt)."""
    df = _analyzable(data["exp0"])
    rates = _discounting_rates(df)
    rates["disc_score"] = rates[["gain_disc", "loss_disc"]].mean(axis=1)
    assets = (
        df[["participant_id", "Q26_3"]]
        .drop_duplicates("participant_id")
        .set_index("participant_id")["Q26_3"]
    )
    d = pd.concat([rates["disc_score"], assets], axis=1).dropna()
    if len(d) < 20:
        return {"effect_name": "assets_discounting", "experiment": "exp0",
                "original_effect_size": -0.05, "effect_size": np.nan, "reproduced": False}
    rho = stats.spearmanr(d["Q26_3"], d["disc_score"])
    reproduced = bool(rho.statistic < 0 and rho.pvalue < 0.05)
    return {
        "effect_name": "assets_discounting",
        "experiment": "exp0",
        "original_effect_size": -0.05,
        "effect_size": float(rho.statistic),
        "p_value": float(rho.pvalue),
        "reproduced": reproduced,
    }


EFFECTS = [check_sign_effect, check_absolute_magnitude, check_assets_discounting]


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
