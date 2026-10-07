# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Brändle, Stocks, Tenenbaum, Gershman &
Schulz (2023), "Empowerment contributes to exploration behaviour in a creative
video game", Nature Human Behaviour 7, 1481-1489, against any dataset in the
Psych-301 unified schema (see schema.md). The local CSVs are the two controlled
online games: exp0 = Tiny Alchemy (semantic), exp1 = Tiny Pixels (non-semantic,
scrambled). Empowerment of an element is estimated from the gameplay itself: the
number of distinct elements it is observed to produce across all players' trials
(number of "offspring"), matching the paper's empowerment definition.

Effects tested:
- immediate_usage_empowerment (exp0/exp1): per-element linear regression of
  immediate-usage probability on empowerment (controlling trials & inventory).
  Expected: strong positive effect in Tiny Alchemy (semantic), absent/negative in
  Tiny Pixels -- i.e. semantics drive immediate use of empowering elements.
- choice_regression_empowerment (exp0/exp1): logistic choice regression comparing
  the chosen combination against a randomly sampled alternative from the player's
  inventory on a delta-empowerment regressor. Expected: empowerment predicts
  choices more in Tiny Alchemy than in Tiny Pixels.
- semantics_performance (exp0/exp1): independent t-tests -- Tiny Alchemy players
  play more trials and create more elements than Tiny Pixels players.
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.api import Logit, OLS, add_constant

EXPERIMENTS = ["exp0", "exp1"]

BASE_ESTIMATE = 4  # each participant starts with 4 base elements


def _load_one(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["first"] = df["first"].astype(int)
    df["second"] = df["second"].astype(int)
    df["success"] = df["success"].astype(int)
    outs = []
    for r in df["results"]:
        try:
            outs.append(int(json.loads(r)[0]))
        except Exception:
            outs.append(-1)
    df["observed_out"] = outs
    df["created"] = (df["observed_out"] >= 0).astype(int)
    return df


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD.

    Required columns:
      exp0: participant_id, trial, first, second, success, results, inventory
      exp1: participant_id, trial, first, second, success, results, inventory
    """
    sources = sources or {}
    return {
        exp: _load_one(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS
    }


def _empowerment(df: pd.DataFrame) -> dict[int, int]:
    """Empowerment (number of distinct elements an element can lead to) estimated
    from the observed combos of a game across all participants."""
    e: dict[int, set[int]] = {}
    done = df[df["created"] == 1]
    for _, row in done.iterrows():
        for el in (int(row["first"]), int(row["second"])):
            e.setdefault(el, set()).add(int(row["observed_out"]))
    return {k: len(v) for k, v in e.items()}


def _base_elements(df: pd.DataFrame) -> set[int]:
    """The base elements are those used but never created (their index never
    appears as an outcome)."""
    created = set(int(o) for o in df[df.created == 1].observed_out)
    used = set(int(x) for x in df.first).union(int(x) for x in df.second)
    return used - created


def check_immediate_usage_empowerment(
    data: dict[str, pd.DataFrame],
) -> dict:
    """"Next, we compared the frequency of immediately using a newly created
    element based on its empowerment value... In 'Tiny Alchemy', players were
    more likely to use empowering elements immediately than in 'Tiny Pixels'
    ('Tiny Alchemy' human: beta=0.42, t=8.51, P<0.001; 'Tiny Pixels' human:
    beta=-0.05, t=-0.55, P=0.58)" - Fine et al. (2023, Nature Human Behaviour),
    The importance of semantic structure, p.1487."""
    betas = {}
    sig_pos = {}
    for exp, df in data.items():
        emp = _empowerment(df)
        info: dict[int, list] = {}
        rows = []
        for _, gp in df.sort_values(["participant_id", "trial"]).groupby(
            "participant_id"
        ):
            gp = gp.reset_index(drop=True)
            for i in range(len(gp) - 1):
                if gp.loc[i, "created"] == 1:
                    el = int(gp.loc[i, "observed_out"])
                    info.setdefault(el, []).append(
                        (gp.loc[i, "trial"], gp.loc[i, "inventory"])
                    )
                    imm = 1 if el in (gp.loc[i + 1, "first"], gp.loc[i + 1, "second"]) else 0
                    rows.append((el, imm))
        ag = pd.DataFrame(rows, columns=["el", "imm"]).groupby("el").agg(
            found=("imm", "count"), used=("imm", "sum")
        )
        ag["usage_prob"] = 100.0 * ag["used"] / ag["found"]
        ag["emp"] = [emp.get(e, 0) for e in ag.index]
        ag["tri_ave"] = [float(np.mean([t for t, _ in info[e]])) for e in ag.index]
        ag["inv_ave"] = [float(np.mean([v for _, v in info[e]])) for e in ag.index]
        X = ag[["emp", "tri_ave", "inv_ave"]].apply(lambda c: c / c.std())
        fit = OLS(ag["usage_prob"], add_constant(X)).fit()
        betas[exp] = float(fit.params["emp"])
        sig_pos[exp] = bool(fit.params["emp"] > 0 and fit.pvalues["emp"] < 0.05)
    alchemy_ok = sig_pos["exp0"]                 # semantic: positive & significant
    pixels_ok = not sig_pos["exp1"]              # non-semantic: no positive sig effect
    reproduced = bool(alchemy_ok and pixels_ok)
    return {
        "effect_name": "immediate_usage_empowerment",
        "experiment": "exp0/exp1",
        "original_effect_size": 0.42,            # Tiny Alchemy human beta
        "effect_size": betas["exp0"],            # local Tiny Alchemy controlled beta
        "alchemy_beta": betas["exp0"],
        "pixels_beta": betas["exp1"],
        "reproduced": reproduced,
    }


def check_choice_regression_empowerment(
    data: dict[str, pd.DataFrame],
) -> dict:
    """"For 'Tiny Alchemy', players were best explained by a combination between
    exploration as empowerment (beta=0.30, z=29.68, P<0.001)... For 'Tiny
    Pixels', players' choices were only significantly positively influenced by
    uncertainty... but we found no evidence for empowerment (beta=-0.05)"
    - Fine et al. (2023, Nature Human Behaviour), Regression analysis for
    experimental data, p.1487. (Original-game headline: empowerment beta=0.38,
    larger than uncertainty beta=0.22.)"""
    rng = np.random.default_rng(0)
    emp_b = {}
    for exp, df in data.items():
        emp = _empowerment(df)
        base = _base_elements(df)
        rows = []
        for _, gp in df.sort_values(["participant_id", "trial"]).groupby(
            "participant_id"
        ):
            gp = gp.reset_index(drop=True)
            inventory = set(base)
            uses: dict[int, int] = {}

            def empc(c):
                return (emp.get(c[0], 0) + emp.get(c[1], 0)) / 2.0

            def unc(c):
                return np.mean([1.0 / (uses.get(el, 0) + 1) for el in c])

            for i in range(len(gp)):
                ch = (int(gp.loc[i, "first"]), int(gp.loc[i, "second"]))
                pool = list(inventory)
                if len(pool) < 2:
                    break
                alt = tuple(rng.choice(pool, 2, replace=False))
                de = empc(ch) - empc(alt)
                du = unc(ch) - unc(alt)
                rows.append((1, de, du))
                rows.append((0, -de, -du))
                for el in ch:
                    uses[el] = uses.get(el, 0) + 1
                if gp.loc[i, "created"]:
                    inventory.add(int(gp.loc[i, "observed_out"]))
        D = pd.DataFrame(rows, columns=["decision", "de", "du"])
        X = add_constant(D[["de", "du"]])
        emph = Logit(D["decision"], X).fit(disp=0)
        emp_b[exp] = float(emph.params["de"])
    alchemy_pos = emp_b["exp0"] > 0
    semantic_advantage = emp_b["exp0"] > emp_b["exp1"]
    reproduced = bool(alchemy_pos and semantic_advantage)
    return {
        "effect_name": "choice_regression_empowerment",
        "experiment": "exp0/exp1",
        "original_effect_size": 0.38,            # original-game empowerment beta
        "effect_size": emp_b["exp0"],            # local Tiny Alchemy empowerment beta
        "alchemy_emp_beta": emp_b["exp0"],
        "pixels_emp_beta": emp_b["exp1"],
        "reproduced": reproduced,
    }


def check_semantics_performance(data: dict[str, pd.DataFrame]) -> dict:
    """"Players of the game 'Tiny Alchemy' played on average longer
    (t(193)=7.12, P<0.001, d=1.02) and discovered more elements (t(193)=7.21,
    P<0.001, d=1.03) than players of the game 'Tiny Pixels' (mean trials: 465.55
    vs 159.44; mean elements: 89.07 vs 27.5)" - Fine et al. (2023, Nature Human
    Behaviour), Behavioural differences, p.1487."""
    ta = data["exp0"]
    tp = data["exp1"]
    ta_trials = ta.groupby("participant_id").trial.max().values + 1
    tp_trials = tp.groupby("participant_id").trial.max().values + 1
    ta_elems = ta.groupby("participant_id")["created"].sum().values
    tp_elems = tp.groupby("participant_id")["created"].sum().values
    t_tri, p_tri = stats.ttest_ind(ta_trials, tp_trials, equal_var=True)
    t_el, p_el = stats.ttest_ind(ta_elems, tp_elems, equal_var=True)
    reproduced = bool(
        ta_trials.mean() > tp_trials.mean()
        and ta_elems.mean() > tp_elems.mean()
        and p_tri < 0.05
        and p_el < 0.05
    )
    return {
        "effect_name": "semantics_performance",
        "experiment": "exp0/exp1",
        "original_effect_size": 7.21,            # paper t for elements
        "effect_size": float(t_el),             # local t for elements
        "trials_t": float(t_tri),
        "elements_t": float(t_el),
        "alchemy_trials": float(ta_trials.mean()),
        "pixels_trials": float(tp_trials.mean()),
        "alchemy_elements": float(ta_elems.mean()),
        "pixels_elements": float(tp_elems.mean()),
        "reproduced": reproduced,
    }


EFFECTS = [
    check_immediate_usage_empowerment,
    check_choice_regression_empowerment,
    check_semantics_performance,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. No printing."""
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None, help=f"CSV path for {exp}")
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS if getattr(args, exp)}
    for exp in EXPERIMENTS:
        print(f"{exp}: {sources[exp] if exp in sources else '(default — local ./{exp}.csv)'}")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<8}  {'orig':>10}  {'this':>10}  reproduced")
    for r in results:
        print(
            f"{r['effect_name']:<{w}}  {r['experiment']:<8}  "
            f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
            f"{'YES' if r['reproduced'] else 'NO'}"
        )


if __name__ == "__main__":
    main()