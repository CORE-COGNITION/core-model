# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Guenther & Marelli (2022), "Patterns in
CAOSS: Distributed representations predict variation in relational interpretations
for familiar and novel compound words", Cognitive Psychology, against any dataset in
the Psych-301 unified schema (see schema.md).

Effects tested:
- catch_trial_accuracy (exp0): the four embedded catch trials (snow man, stone ware,
  sweat band, tea time) have well-defined normative answers; participants answer them
  at far above the 1/16 chance level, and only 34 of 400 (8.5%) participants are
  non-compliant (<3 of 4 correct). Test: binomial proportion vs. chance; direction:
  accuracy >> chance.
- relations_systematic_nonuniform (exp0): across the 16 possible relational
  interpretations, participants' choices are strongly non-uniform / systematic rather
  than random. Test: chi-square goodness-of-fit of the pooled relation counts against
  a uniform distribution; direction: observed distribution differs strongly from
  uniform, top relation far above the 1/16 chance share.
- high_interpretational_variability (exp0): item-level relational entropy of the 408
  novel compounds is high (paper reports M = 2.338), i.e., participants do not converge
  on a single relation but spread across several — substantial across-subject
  variation. Test: one-sample t-test that mean item entropy exceeds a near-unanimous
  baseline; direction: entropy clearly > 0 / > 1, p < .05.
"""
from __future__ import annotations

import argparse
from collections import Counter

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD — `cd` into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      exp0: participant_id, trial, response  (and: type, stim)
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def check_catch_trial_accuracy(data: dict[str, pd.DataFrame]) -> dict:
    """\"In addition, each list contained four catch trials aimed at identifying
    non-compliant participants ... A participant was considered non-compliant if
    fewer than 3 out of 4 of their responses to the catch trials were classified as
    correct, which was the case for 34 participants.\" — Guenther & Marelli, 2022,
    p.10, Experiment 2: Method/Procedure & Results."""
    df = data["exp0"]
    if "type" not in df.columns or "catch" not in df["type"].astype(str).unique():
        return {
            "effect_name": "catch_trial_accuracy",
            "experiment": "exp0",
            "original_effect_size": 0.085,
            "effect_size": float("nan"),
            "reproduced": False,
        }
    norm = {
        "snow man": "H_made_of_M",
        "stone ware": "H_made_of_M",
        "sweat band": "H_for_M",
        "tea time": "H_for_M",
    }
    catch = df[df["type"].astype(str).eq("catch")].copy()
    items_present = [k for k in norm if catch["stim"].astype(str).str.lower().eq(k).any()]
    if not items_present:
        return {
            "effect_name": "catch_trial_accuracy",
            "experiment": "exp0",
            "original_effect_size": 0.085,
            "effect_size": float("nan"),
            "reproduced": False,
        }
    catch["_good"] = False
    modal_matches = 0
    for key in items_present:
        m = catch["stim"].astype(str).str.lower().eq(key)
        sub = catch[m]
        vc = sub["response"].value_counts()
        conv = set(vc[vc >= 10].index)
        good = {norm[key]}.union(conv)
        catch.loc[m, "_good"] = catch.loc[m, "response"].isin(good).values
        modal_matches += int(sub["response"].mode().iat[0] == norm[key])
    n_total = len(catch)
    k_correct = int(catch["_good"].sum())
    accuracy = k_correct / n_total
    p_binom = stats.binomtest(k_correct, n_total, 1 / 16).pvalue
    compliant = catch.groupby("participant_id")["_good"].mean()
    prop_noncompliant = float((compliant < 0.75).mean())
    reproduced = bool(
        accuracy > 0.5 and p_binom < 0.05 and modal_matches == len(items_present)
        and prop_noncompliant < 0.5
    )
    return {
        "effect_name": "catch_trial_accuracy",
        "experiment": "exp0",
        "original_effect_size": 0.085,
        "effect_size": float(prop_noncompliant),
        "reproduced": reproduced,
    }


def check_relations_systematic_nonuniform(data: dict[str, pd.DataFrame]) -> dict:
    """\"Variations in qualitative meaning interpretations can be directly quantified
    via distributions over the closed set of possible relational structures ... for
    completely novel combinations ('swordbird').\" — Guenther & Marelli, 2022, p.4,
    Introduction. The paper models these distributions on the premise that choices are
    systematic (organized around a few dominant relations), not uniform random."""
    df = data["exp0"]
    if "type" in df.columns:
        d = df[~df["type"].astype(str).isin(["catch", "practice", "training"])]
    else:
        d = df
    counts = d["response"].value_counts()
    obs = counts.values.astype(float)
    k = len(obs)
    top_share = float(obs.max() / obs.sum())
    chi2, p = stats.chisquare(obs, f_exp=np.full(k, obs.sum() / k))
    reproduced = bool((p < 0.05) and (top_share > 2 * (1 / k)))
    return {
        "effect_name": "relations_systematic_nonuniform",
        "experiment": "exp0",
        "original_effect_size": 1 / 16,
        "effect_size": float(top_share),
        "reproduced": reproduced,
    }


def check_high_interpretational_variability(data: dict[str, pd.DataFrame]) -> dict:
    """\"the relational entropy ... of the 408 novel compounds in Experiment 2 was
    higher on average than for the 575 familiar compounds in Experiment 1
    (M2 = 2.338 vs M1 = 2.131, t(797) = -4.97, p < .001), indicating higher
    interpretational variability in novel compounds as compared to existing
    compounds.\" — Guenther & Marelli, 2022, p.10, Experiment 2: Results. Here we
    check the absolute level on the novel-compound side only (no Experiment-1 data is
    present in the local CSV): entropy must be clearly high, i.e. well above a
    near-unanimous baseline."""
    df = data["exp0"]
    if "type" in df.columns:
        d = df[~df["type"].astype(str).isin(["catch", "practice", "training"])]
    else:
        d = df

    def entropy(s: pd.Series) -> float:
        p = s.value_counts(normalize=True).values
        p = p[p > 0]
        return float(-np.sum(p * np.log(p)))

    ent = d.groupby("stim")["response"].apply(entropy)
    mean_ent = float(ent.mean())
    t, p = stats.ttest_1samp(ent, 1.0)
    reproduced = bool((mean_ent > 1.0) and (p < 0.05))
    return {
        "effect_name": "high_interpretational_variability",
        "experiment": "exp0",
        "original_effect_size": 2.338,
        "effect_size": float(mean_ent),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_catch_trial_accuracy,
    check_relations_systematic_nonuniform,
    check_high_interpretational_variability,
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
