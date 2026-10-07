# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Vandendriessche et al. (2022/2023,
"Contextual influence of reinforcement learning performance of depression:
evidence for a negativity bias?", Psychological Medicine 53(10):4696-4706)
against any dataset in the Psych-301 unified schema (see schema.md).

Two-phase contextual two-armed bandit (rich vs poor context) with a transfer
phase. 56 participants (30 patients, 26 controls); both phases live in exp0
(`phase` = learning vs transfer).

Effects tested:
- learning_accuracy_above_chance (exp0): overall learning-phase correct
  response rate significantly above chance (GLMM intercept; one-sample t-test
  of per-participant accuracy vs 0.5). Expected: mean > 0.5, p < .05.
- learning_context_group_interaction (exp0): context x group interaction on
  learning accuracy — patients learn less in the 'poor' than the 'rich'
  context while controls do not (independent-samples contrast of each
  participant's (rich - poor) accuracy across groups + within-group
  rich-vs-poor paired tests). Expected: group contrast p < .05 and within
  patients rich > poor.
- transfer_seeking_vs_avoiding (exp0): in the no-feedback transfer phase,
  group x context interaction on correct response in trials involving the
  best option 'A' (seek) vs the worst option 'D' (avoid): patients are
  better at seeking A than avoiding D, controls are statistically equal
  (independent-samples contrast of (A-present - D-present) accuracy across
  groups + within-group paired tests). Expected: group contrast p < .05 and
  within patients A-present > D-present.
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0"]

# Harmonization of the transfer-phase stimulus identities (symbols 5-8 are the
# session-2 set with equal expected values to 1-4; A=1 best ... D=4 worst),
# applied exactly as in the paper's analysis script (data_depression.Rmd).
_HARMONIZE = {5: 1, 6: 2, 7: 3, 8: 4}
_HARMONIZE_S1 = {3: 1, 4: 2, 1: 3, 2: 4}


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD — `cd` into a checkout of the dataset repo (or
    pass --<exp> path on the CLI) before running.

    Required columns per experiment:
      exp0: participant_id, group, phase, context, correct, response,
            symbol_left, symbol_right
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _harmonize(series: pd.Series) -> pd.Series:
    s = series.map(_HARMONIZE).fillna(series)
    return s.map(_HARMONIZE_S1).fillna(s).astype(float)


def _transfer_good_targets(df: pd.DataFrame) -> pd.DataFrame:
    """Add harmonized symbol values and 'is this the better option?' coding."""
    tr = df.copy()
    tr["s_left"] = _harmonize(tr["symbol_left"])
    tr["s_right"] = _harmonize(tr["symbol_right"])
    tr["good"] = np.where(
        tr["s_left"] == tr["s_right"], np.nan,
        np.where((tr["response"] == 0) & (tr["s_left"] < tr["s_right"]), 1.0,
                 np.where((tr["response"] == 1) & (tr["s_left"] > tr["s_right"]), 1.0, 0.0)))
    return tr


def check_learning_accuracy_above_chance(data: dict[str, pd.DataFrame]) -> dict:
    """"Correct response rate (as proxied by the intercept of our GLMM) in the
    learning phase (Figure 2A) indicated that overall performance is
    significantly above chance (χ2(1,56)=16.17 , p<0.001)" — Vandendriessche et
    al., Results, Learning phase results."""
    df = data["exp0"]
    req = ["participant_id", "phase", "correct"]
    if not set(req).issubset(df.columns):
        return {"effect_name": "learning_accuracy_above_chance", "experiment": "exp0",
                "original_effect_size": np.nan, "effect_size": np.nan,
                "reproduced": False, "notes": "missing required columns"}
    learn = df[(df["phase"] == "learning") & df["correct"].notna()] if "phase" in df.columns else df[df["correct"].notna()]
    acc = learn.groupby("participant_id")["correct"].mean()
    t, p = stats.ttest_1samp(acc.values.astype(float), 0.5)
    reproduced = bool(acc.mean() > 0.5 and p < 0.05)
    return {
        "effect_name": "learning_accuracy_above_chance",
        "experiment": "exp0",
        "original_effect_size": float(np.sqrt(16.17)),  # paper chi2(1)=16.17 -> t
        "effect_size": float(t),
        "mean_accuracy": float(acc.mean()),
        "p": float(p),
        "reproduced": reproduced,
    }


def check_learning_context_group_interaction(data: dict[str, pd.DataFrame]) -> dict:
    """"there was a significant interaction between context and group
    (χ2(1,56)=5.88 , p=0.015). [...] driven by an effect of context present in
    patients (slope=-0.72 , SE=0.24 , p<0.0027), but not in controls (slope=
    -0.063 , SE=0.29 , p=0.83)" — Vandendriessche et al., Results, Learning
    phase results."""
    df = data["exp0"]
    req = ["participant_id", "group", "context", "phase", "correct"]
    if not set(req).issubset(df.columns):
        return {"effect_name": "learning_context_group_interaction", "experiment": "exp0",
                "original_effect_size": np.nan, "effect_size": np.nan,
                "reproduced": False, "notes": "missing required columns"}
    learn = df[df["phase"] == "learning"]
    cell = learn.groupby(["participant_id", "group", "context"])["correct"].mean().reset_index()
    wide = cell.pivot_table(index="participant_id", columns="context", values="correct")
    for c in ("rich", "poor"):
        if c not in wide.columns:
            return {"effect_name": "learning_context_group_interaction", "experiment": "exp0",
                    "original_effect_size": np.nan, "effect_size": np.nan,
                    "reproduced": False, "notes": "missing rich/poor context"}
    wide["diff"] = wide["rich"] - wide["poor"]
    gmap = cell.drop_duplicates("participant_id").set_index("participant_id")["group"]
    wide["group"] = wide.index.map(gmap)
    pat = wide[wide["group"] == "patient"]
    con = wide[wide["group"] == "control"]
    t_int, p_int = stats.ttest_ind(pat["diff"], con["diff"], equal_var=False)
    t_pat, p_pat = stats.ttest_rel(pat["rich"], pat["poor"])
    reproduced = bool(p_int < 0.05 and pat["diff"].mean() > 0 and t_pat > 0 and p_pat < 0.05)
    return {
        "effect_name": "learning_context_group_interaction",
        "experiment": "exp0",
        "original_effect_size": float(np.sqrt(5.88)),  # paper chi2(1)=5.88 -> t
        "effect_size": float(t_int),
        "p_interaction": float(p_int),
        "reward_patients_rich_minus_poor": float(pat["diff"].mean()),
        "reproduced": reproduced,
    }


def check_transfer_seeking_vs_avoiding(data: dict[str, pd.DataFrame]) -> dict:
    """"a very strong and significant group by context interaction
    (χ2(1,56)=53.21 , p<0.001). Post-hoc tests reveal that controls were
    equally able to make the correct decision in contexts involving seeking 'A'
    or those involving avoiding 'D' (slope=-0.004 , SE=0.1 , p=0.999) whereas
    patients were strikingly better at seeking 'A' than avoiding 'D'
    (slope=1.06 , SE=0.1 , p<0.001)" — Vandendriessche et al., Results,
    Transfer phase analysis."""
    df = data["exp0"]
    req = ["participant_id", "group", "phase", "response", "symbol_left", "symbol_right"]
    if not set(req).issubset(df.columns):
        return {"effect_name": "transfer_seeking_vs_avoiding", "experiment": "exp0",
                "original_effect_size": np.nan, "effect_size": np.nan,
                "reproduced": False, "notes": "missing required columns"}
    tr = _transfer_good_targets(df[df["phase"] == "transfer"])
    tr = tr[tr["good"].notna()]
    s = tr["s_left"].to_numpy()
    a_present = ((s == 1) & (tr["s_right"] != 4)) | ((tr["s_right"] == 1) & (s != 4))
    d_present = ((s == 4) & (tr["s_right"] != 1)) | ((tr["s_right"] == 4) & (s != 1))
    tr["ctx"] = np.select([a_present, d_present], ["A present", "D present"], default="other")
    subset = tr[tr["ctx"].isin(["A present", "D present"])]
    cell = subset.groupby(["participant_id", "group", "ctx"])["good"].mean().reset_index()
    wide = cell.pivot_table(index="participant_id", columns="ctx", values="good")
    if not {"A present", "D present"}.issubset(wide.columns):
        return {"effect_name": "transfer_seeking_vs_avoiding", "experiment": "exp0",
                "original_effect_size": np.nan, "effect_size": np.nan,
                "reproduced": False, "notes": "missing A/D-present trials"}
    wide["diff"] = wide["A present"] - wide["D present"]
    gmap = cell.drop_duplicates("participant_id").set_index("participant_id")["group"]
    wide["group"] = wide.index.map(gmap)
    pat = wide[wide["group"] == "patient"]
    con = wide[wide["group"] == "control"]
    t_int, p_int = stats.ttest_ind(pat["diff"], con["diff"], equal_var=False)
    t_pat, p_pat = stats.ttest_rel(pat["A present"], pat["D present"])
    t_con, p_con = stats.ttest_rel(con["A present"], con["D present"])
    reproduced = bool(p_int < 0.05 and pat["diff"].mean() > 0 and t_pat > 0
                      and p_pat < 0.05 and p_con > 0.05)
    return {
        "effect_name": "transfer_seeking_vs_avoiding",
        "experiment": "exp0",
        "original_effect_size": float(np.sqrt(53.21)),  # paper chi2(1)=53.21 -> t
        "effect_size": float(t_int),
        "p_interaction": float(p_int),
        "patients_seek_minus_avoid": float(pat["diff"].mean()),
        "reproduced": reproduced,
    }


EFFECTS = [check_learning_accuracy_above_chance,
           check_learning_context_group_interaction,
           check_transfer_seeking_vs_avoiding]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. No printing — pure return
    value so downstream simulators / model evaluators can call this
    programmatically."""
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