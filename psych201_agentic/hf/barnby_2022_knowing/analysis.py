# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Barnby, Raihani & Dayan (2022),
"Knowing me, knowing you: Interpersonal similarity improves predictive accuracy
and reduces attributions of harmful intent" against any dataset in the Psych-301
unified schema (see schema.md).

Effects tested:
- paranoia_reduces_prosocial_choices (exp0): In Phase 1 (decider), the proportion of
  prosocial choices in prosocial-vs-competitive pairs is regressed on paranoia
  (R-GPTS-B); expected negative slope, p < .05.
- partner_alignment_improves_accuracy (exp0): In Phase 2 (recipient), participants
  whose own SVO matches their partner's are expected to have higher predictive
  accuracy (total correct / 36) than misaligned participants; positive slope on an
  aligned indicator, p < .05.
- partner_alignment_reduces_harmful_intent (exp0): In Phase 2, aligned participants
  are expected to attribute less harmful intent (0-100 rating, the `hi` column) to
  their partner than misaligned participants; negative slope, p < .05.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD; pass --<exp> path on the CLI to override.

    Required columns:
      exp0: participant_id, trial, phase, condition, response, type1, type2,
            choice, correct, persec, hi
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _own_svo(df: pd.DataFrame) -> pd.Series:
    """Per-participant own SVO type, from the modal Phase-1 (decider) choice."""
    d = df[df["phase"] == "decider"].copy()
    d["choice"] = d["choice"].astype(str).str.lower().str.replace("competitive", "competative")
    return d.groupby("participant_id")["choice"].agg(lambda x: x.value_counts().idxmax()).rename("own")


def check_paranoia_reduces_prosocial_choices(data: dict[str, pd.DataFrame]) -> dict:
    """\"More paranoid people made fewer prosocial choices, both in the
    prosocial-competitive choice pairs (non-averaged estimate = -0.08, 95%CI:
    -0.10, -0.06 ... Model 1a)\" — Barnby et al., 2022, p.13, Section 3.2.1."""
    df = data["exp0"]
    d = df[df["phase"] == "decider"].copy()
    t1 = d["type1"].astype(str).str.lower().str.replace("competitive", "competative")
    t2 = d["type2"].astype(str).str.lower().str.replace("competitive", "competative")
    pc = d[((t1 == "prosocial") & (t2 == "competative")) | ((t1 == "competative") & (t2 == "prosocial"))]
    prop = pc.groupby("participant_id")["choice"].apply(
        lambda x: (x.astype(str).str.lower().str.replace("competitive", "competative") == "prosocial").mean()
    )
    paranoia = df[df["phase"] == "recipient"].drop_duplicates("participant_id").set_index("participant_id")["persec"]
    dfm = prop.to_frame("prop").join(paranoia).dropna()
    res = stats.linregress(dfm["persec"], dfm["prop"])
    effect_size = float(res.slope)
    original_effect_size = -0.08
    reproduced = bool((effect_size < 0) and (res.pvalue < 0.05))
    return {
        "effect_name": "paranoia_reduces_prosocial_choices",
        "experiment": "exp0",
        "original_effect_size": original_effect_size,
        "effect_size": effect_size,
        "pvalue": float(res.pvalue),
        "reproduced": reproduced,
    }


def _aligned_frame(df: pd.DataFrame) -> pd.DataFrame:
    d = df[df["phase"] == "decider"].copy()
    r = df[df["phase"] == "recipient"].copy()
    own = _own_svo(d)
    r2 = r.merge(own, on="participant_id")
    part = r2["condition"].astype(str).str.lower().str.replace("competitive", "competative")
    r2["aligned"] = (r2["own"] == part).astype(int)
    per = r2.reset_index(drop=True).set_index("participant_id")
    out = per.groupby(per.index).first()[["aligned"]].copy()
    out["acc"] = r.groupby("participant_id")["correct"].mean() * 36
    out["hi"] = per.groupby(per.index)["hi"].first().astype(float)
    return out


def check_partner_alignment_improves_accuracy(data: dict[str, pd.DataFrame]) -> dict:
    """\"Alignment ... was associated with better predictions\" — Barnby et al.,
    2022, Abstract (p.2); predictive accuracy positively associated with baseline
    similarity (Model 7, estimate ~0.19, 95%CI 0.12-0.27)."""
    a = _aligned_frame(data["exp0"]).dropna(subset=["aligned", "acc"])
    res = stats.linregress(a["aligned"], a["acc"])
    effect_size = float(res.slope)
    original_effect_size = 0.19
    reproduced = bool((effect_size > 0) and (res.pvalue < 0.05))
    return {
        "effect_name": "partner_alignment_improves_accuracy",
        "experiment": "exp0",
        "original_effect_size": original_effect_size,
        "effect_size": effect_size,
        "pvalue": float(res.pvalue),
        "reproduced": reproduced,
    }


def check_partner_alignment_reduces_harmful_intent(data: dict[str, pd.DataFrame]) -> dict:
    """\"Misalignment of social values resulted in larger attributions of harmful
    intent\" — Barnby et al., 2022, Highlights (p.2) / Abstract."""
    a = _aligned_frame(data["exp0"]).dropna(subset=["aligned", "hi"])
    res = stats.linregress(a["aligned"], a["hi"])
    effect_size = float(res.slope)
    original_effect_size = -1.0  # aligned -> lower HI (direction)
    reproduced = bool((effect_size < 0) and (res.pvalue < 0.05))
    return {
        "effect_name": "partner_alignment_reduces_harmful_intent",
        "experiment": "exp0",
        "original_effect_size": original_effect_size,
        "effect_size": effect_size,
        "pvalue": float(res.pvalue),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_paranoia_reduces_prosocial_choices,
    check_partner_alignment_improves_accuracy,
    check_partner_alignment_reduces_harmful_intent,
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
    print(f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()
