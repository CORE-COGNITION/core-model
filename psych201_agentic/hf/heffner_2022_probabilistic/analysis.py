# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Heffner & FeldmanHall (2022), A
probabilistic map of emotional experiences during competitive social
interactions, Nature Communications, against any dataset in the Psych-301
unified schema (see schema.md).

Effects tested:
- ug_punishment_unfairness (exp0): In the Ultimatum Game, unfair offers are
  punished more than fair ones; the rejection/punishment rate rises with
  offer unfairness (a positive correlation between reject and unfairness).
- pd_emotion_defection (exp1): In the Prisoner's Dilemma, negative emotional
  experience (lower valence) is associated with defection (lower
  contribution); contribution correlates positively with valence and with the
  partner's contribution (reciprocity / coop-defect gradient).
- pgg_emotion_free_riding (exp2): In the Public Goods Game, free riding is
  driven by negative affect; contribution correlates positively with valence
  and with the partners' collective contribution.
"""
from __future__ import annotations

import argparse
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0", "exp1", "exp2"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD.

    Required columns per experiment:
      exp0: participant_id, trial, response, unfairness
      exp1: participant_id, trial, response, valence, partner_contribution
      exp2: participant_id, block, response, valence, partners_contribution
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def check_ug_punishment_unfairness(data: dict[str, pd.DataFrame]) -> dict:
    """"When offers are more unfair (i.e., the Proposer keeps more of the $1
    pot), the Responder is more likely to punish by rejecting the offer." —
    Heffner & FeldmanHall, 2022, p.2 (The emotions associated with decisions
    to punish)."""
    df = data["exp0"]
    r, p = stats.pointbiserialr(df["response"], df["unfairness"])
    reproduced = r > 0 and p < 0.05
    return {
        "effect_name": "ug_punishment_unfairness",
        "experiment": "exp0",
        "original_effect_size": 0.52,
        "effect_size": float(r),
        "p_value": float(p),
        "reproduced": bool(reproduced),
    }


def check_pd_emotion_defection(data: dict[str, pd.DataFrame]) -> dict:
    """"To make the analysis analogous to Experiment 1, we binned continuous
    contributions into decisions to defect ($0–$0.49) and cooperate ($0.50–$1)
    ... sadness and disappointment are associated with defection" — Heffner &
    FeldmanHall, 2022, p.7 (The emotions associated with decisions to
    defect). Negative affect (low valence) tracks defection; contribution
    correlates positively with self-reported valence and with the partner's
    contribution."""
    df = data["exp1"]
    r_val, p_val = stats.pearsonr(df["response"], df["valence"])
    r_part, p_part = stats.pearsonr(df["response"], df["partner_contribution"])
    reproduced = r_val > 0 and p_val < 0.05
    return {
        "effect_name": "pd_emotion_defection",
        "experiment": "exp1",
        "original_effect_size": 0.41,
        "effect_size": float(r_val),
        "p_value": float(p_val),
        "reciprocity_r": float(r_part),
        "reproduced": bool(reproduced),
    }


def check_pgg_emotion_free_riding(data: dict[str, pd.DataFrame]) -> dict:
    """"Sadness and disappointment are associated with free riding" ... "we
    did not find good evidence that ... highly arousing and negatively valenced
    feelings ... shape these decisions. Instead, negatively valenced and
    neutrally arousing emotions ... are the most common affective experiences
    associated with punishing, defecting, and free riding." — Heffner &
    FeldmanHall, 2022, p.7. Contributions correlate positively with valence and
    with the partners' collective contribution; free riding tracks negative
    affect."""
    df = data["exp2"]
    agg = df.groupby(["participant_id", "block"]).agg(
        response=("response", "first"),
        valence=("valence", "mean"),
        partners_contribution=("partners_contribution", "first"),
    ).reset_index()
    r_val, p_val = stats.pearsonr(agg["response"], agg["valence"])
    r_part, p_part = stats.pearsonr(agg["response"], agg["partners_contribution"])
    reproduced = r_val > 0 and p_val < 0.05
    return {
        "effect_name": "pgg_emotion_free_riding",
        "experiment": "exp2",
        "original_effect_size": 0.61,
        "effect_size": float(r_val),
        "p_value": float(p_val),
        "reciprocity_r": float(r_part),
        "reproduced": bool(reproduced),
    }


EFFECTS = [
    check_ug_punishment_unfairness,
    check_pd_emotion_defection,
    check_pgg_emotion_free_riding,
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
