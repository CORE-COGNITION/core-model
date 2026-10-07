# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "scipy"]
# ///
"""Check the primary behavioral effects of Chambon, Théro, Vidal, Vandendriessche, Haggard &
Palminteri (2020), "Information about action outcomes differentially affects learning from
self-determined versus imposed choices", Nat Hum Behav 4, 1067-1079, against any dataset in the
Psych-301 unified schema (see schema.md).

The paper's abstract claims a choice-confirmation bias in reinforcement learning that is specific
to free (self-determined) choices, independent of outcome contingencies (high vs low reward), and
unaffected by motor requirements (go vs no-go). Those analyses rely on model-estimated learning
rates; here we check their behavioral signatures that are directly computable from choice accuracy
(the `response` column = chose the best-rewarded stimulus):
- confirmed free-choice learning (accuracy > chance),
- a benefit when both factual AND counterfactual (chosen + unchosen) outcomes are provided,
- learning under both go and no-go motor requirements.

Effects tested:
- confirmatory_free_choice_learning (exp0): optimal-choice accuracy on freely-chosen trials exceeds
  chance (0.5); paired one-sample t-test, expected direction +.
- counterfactual_feedback_benefit (exp1): free-trial accuracy is higher when both factual and
  counterfactual outcomes are shown (condition_code 2, 4) than when only the factual outcome is
  shown (condition_code 1, 3); paired t-test on per-participant accuracy, expected direction +.
- motor_independence_go_nogo (exp3): optimal-choice accuracy exceeds chance under BOTH go and no-go
  motor requirements; two one-sample t-tests, expected direction + for each.
"""
from __future__ import annotations

import argparse

import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0", "exp1", "exp2", "exp3"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides, loads ./{exp}.csv
    from CWD -- cd into a checkout of the dataset repo (or pass --<exp> path on the CLI) before
    running.

    Required columns per experiment:
      exp0: participant_id, forced_choice, response
      exp1: participant_id, condition_code, forced_choice, response
      exp3: participant_id, go, nogo, response
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _free_acc(df: pd.DataFrame) -> pd.Series:
    d = df[df["forced_choice"] == 0]
    return d.groupby("participant_id")["response"].mean()


def check_confirmatory_free_choice_learning(data: dict[str, pd.DataFrame]) -> dict:
    """\"Analysis of model-estimated learning rates showed that the confirmation bias in learning
    rates was specific to free choices\" -- Chambon et al., 2020, p. 1067, Abstract."""
    df = data["exp0"]
    acc = _free_acc(df).dropna()
    t, p = stats.ttest_1samp(acc, 0.5)
    effect_size = float(acc.mean() - 0.5)
    reproduced = bool(acc.mean() > 0.5 and p < 0.05)
    return {
        "effect_name": "confirmatory_free_choice_learning",
        "experiment": "exp0",
        "original_effect_size": 0.27,
        "effect_size": effect_size,
        "extra": {"mean_acc": float(acc.mean()), "t": float(t), "p": float(p), "n": int(len(acc))},
        "reproduced": reproduced,
    }


def check_counterfactual_feedback_benefit(data: dict[str, pd.DataFrame]) -> dict:
    """\"The confirmation bias in learning rates was specific to free choices, but was independent
    of outcome contingencies\" -- Chambon et al., 2020, p. 1067, Abstract (factual-only vs
    factual+counterfactual feedback conditions of Experiment 2)."""
    df = data["exp1"]
    d = df[df["forced_choice"] == 0]
    fact = d[d["condition_code"].isin([1, 3])].groupby("participant_id")["response"].mean()
    cfact = d[d["condition_code"].isin([2, 4])].groupby("participant_id")["response"].mean()
    a, b = fact.align(cfact)
    t, p = stats.ttest_rel(a, b)
    effect_size = float((b - a).mean())
    reproduced = bool(effect_size > 0 and p < 0.05)
    return {
        "effect_name": "counterfactual_feedback_benefit",
        "experiment": "exp1",
        "original_effect_size": 0.08,
        "effect_size": effect_size,
        "extra": {"factual_only": float(a.mean()), "factual_plus_counterfactual": float(b.mean()),
                  "t": float(t), "p": float(p), "n": int(len(a))},
        "reproduced": reproduced,
    }


def check_motor_independence_go_nogo(data: dict[str, pd.DataFrame]) -> dict:
    """\"The bias was also unaffected by the motor requirements, thus suggesting that it operates in
    the representational space of decisions, rather than motoric actions\" -- Chambon et al., 2020,
    p. 1067, Abstract."""
    df = data["exp3"]
    results = {}
    ok = True
    for label, mask in [("go", df["go"] == 1), ("nogo", df["nogo"] == 1)]:
        d = df[mask]
        acc = d.groupby("participant_id")["response"].mean().dropna()
        t, p = stats.ttest_1samp(acc, 0.5)
        results[label] = {"mean_acc": float(acc.mean()), "t": float(t), "p": float(p),
                          "n": int(len(acc))}
        ok = ok and (acc.mean() > 0.5 and p < 0.05)
    effect_size = float(min(results["go"]["mean_acc"], results["nogo"]["mean_acc"]) - 0.5)
    return {
        "effect_name": "motor_independence_go_nogo",
        "experiment": "exp3",
        "original_effect_size": 0.15,
        "effect_size": effect_size,
        "extra": results,
        "reproduced": bool(ok),
    }


EFFECTS = [
    check_confirmatory_free_choice_learning,
    check_counterfactual_feedback_benefit,
    check_motor_independence_go_nogo,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. No printing -- pure return value."""
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None, help=f"CSV path for {exp}; defaults to ./{exp}.csv in CWD")
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS if getattr(args, exp)}
    for exp in EXPERIMENTS:
        print(f"{exp}: {sources[exp] if exp in sources else '(default -- local ./' + exp + '.csv)'}")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<5}  {'orig':>10}  {'this':>10}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<5}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()