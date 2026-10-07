# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Feher da Silva, Lombardi, Edelson &
Hare (2023), "Rethinking model-based and model-free influences on mental effort
and striatal prediction errors", Nat. Hum. Behav. 7, 956-969, against any dataset
in the Psych-301 unified schema (see schema.md).

The paper is a single two-stage (Daw two-step) fMRI/behavioral study with
between-subjects "abstract" vs "story" instruction conditions. Headline claim:
task instructions generating more correct model-based behaviour reduce rather
than increase mental effort, i.e. model-free learning may not be automatic.

Effects tested:
- model_based_stay (exp0): reward x transition-type interaction on first-stage
  stay (repetition) probability is positive and significant -- the model-based
  signature in the two-step task (Fig 2 logistic regression).
- model_based_weight_story (exp0): the story instruction condition increases
  model-based weighting, i.e. the story x reward x transition interaction on
  stage-1 stay probability is positive and significant ("task instructions
  generating more correct model-based behaviour").
- effort_rating_story (exp0): subjective mental-effort rating is lower in the
  story than the abstract condition ("reduce rather than increase mental effort").
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

EXPERIMENTS = ["exp0"]

# Exact effect sizes from the paywalled Nature article were not retrievable
# (abstract/figures only). Original effect sizes are therefore reported as NaN;
# reproduction is judged on sign + significance as per the paper's claims.
PAPER_NA = float("nan")


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD.

    Required columns per experiment:
      exp0: participant_id, condition, block, stage, slow, choice1, choice2,
            common, reward
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _trial_pairs(df: pd.DataFrame) -> pd.DataFrame:
    """Builds one row per consecutive trial pair on first-stage free choices.

    Matches the paper's stay-probability logistic regression: for each pair,
    stay = 1 if the stage-1 action was repeated, with previous-trial reward and
    transition type coded as -1/+1.
    """
    st1 = df[df["stage"] == "stage1"].copy()
    st1 = st1[st1["slow"] == 0]
    st2 = df[df["stage"] == "stage2"].copy()
    recs = []
    for pid, g in df.groupby("participant_id"):
        s1 = st1[st1["participant_id"] == pid].sort_values("block").reset_index(drop=True)
        if s1.empty:
            continue
        cond = 1 if s1["condition"].iloc[0] == "story" else 0
        choices = s1["choice1"].to_numpy()
        commons = s1["common"].astype(int).to_numpy()
        rmap = st2[st2["participant_id"] == pid].set_index("block")["reward"]
        rew = np.array([rmap[b] for b in s1["block"] if b in rmap.index], dtype=float)
        blocks = np.array([b for b in s1["block"] if b in rmap.index])
        for i in range(1, len(s1)):
            if s1["block"].iloc[i] not in rmap.index or s1["block"].iloc[i - 1] not in rmap.index:
                continue
            if np.isnan(choices[i]) or np.isnan(choices[i - 1]):
                continue
            rew_prev = rmap.get(s1["block"].iloc[i - 1], np.nan)
            if np.isnan(rew_prev):
                continue
            stay = 1.0 if choices[i] == choices[i - 1] else 0.0
            rw = 2.0 * rew_prev - 1.0
            co = 2.0 * commons[i - 1] - 1.0
            recs.append({"pid": pid, "story": cond, "rw": rw, "co": co, "stay": stay})
    out = pd.DataFrame(recs)
    out["rxc"] = out["rw"] * out["co"]
    return out


def _gee_logit(df: pd.DataFrame, xcols: list[str]) -> "tuple":
    """Cluster-robust (per-participant) pooled logistic regression of stay."""
    from statsmodels.genmod.generalized_estimating_equations import GEE
    from statsmodels.genmod.cov_struct import Independence
    from statsmodels.genmod.families import Binomial

    X = sm.add_constant(df[xcols])
    fam = Binomial()
    mdl = GEE(df["stay"], X, groups=df["pid"], family=fam, cov_struct=Independence())
    res = mdl.fit()
    return res, X.columns


def check_model_based_stay(data: dict[str, pd.DataFrame]) -> dict:
    """\"Results of a logistic regression analysis of the stay probability in
    consecutive trial pairs\" --- Feher da Silva et al. 2023, Fig. 2 caption.
    The reward x transition-type (common) interaction on stage-1 stay probability
    is positive and significant (model-based influence); the paper rests on this
    signature being present."""
    df = _trial_pairs(data["exp0"])
    res, cols = _gee_logit(df, ["rw", "co", "rxc"])
    beta = float(res.params.loc["rxc"])
    p = float(res.pvalues.loc["rxc"])
    reproduced = bool(beta > 0 and p < 0.05)
    return {
        "effect_name": "model_based_stay",
        "experiment": "exp0",
        "original_effect_size": PAPER_NA,
        "effect_size": beta,
        "p": p,
        "reproduced": reproduced,
    }


def check_model_based_weight_story(data: dict[str, pd.DataFrame]) -> dict:
    """\"we find that task instructions generating more correct model-based
    behaviour reduce rather than increase mental effort\" --- Feher da Silva
    et al. 2023, Abstract. The story condition produces MORE correct
    model-based behaviour: the story x reward x transition interaction on
    stage-1 stay probability is positive and significant."""
    df = _trial_pairs(data["exp0"])
    df["story_rw"] = df["story"] * df["rw"]
    df["story_co"] = df["story"] * df["co"]
    df["story_rxc"] = df["story"] * df["rxc"]
    res, cols = _gee_logit(df, ["rw", "co", "rxc", "story", "story_rw", "story_co", "story_rxc"])
    beta = float(res.params.loc["story_rxc"])
    p = float(res.pvalues.loc["story_rxc"])
    reproduced = bool(beta > 0 and p < 0.05)
    return {
        "effect_name": "model_based_weight_story",
        "experiment": "exp0",
        "original_effect_size": PAPER_NA,
        "effect_size": beta,
        "p": p,
        "reproduced": reproduced,
    }


def check_effort_rating_story(data: dict[str, pd.DataFrame]) -> dict:
    """\"...task instructions generating more correct model-based behaviour
    reduce rather than increase mental effort\" --- Feher da Silva et al. 2023,
    Abstract (see also Fig. 3, distribution of effort ratings by condition).
    Post-task mental-effort ratings are lower in the story than the abstract
    condition."""
    first = data["exp0"].groupby("participant_id").first()
    first = first[first["effort"].notna()]
    story = first.loc[first["condition"] == "story", "effort"]
    abstract = first.loc[first["condition"] == "abstract", "effort"]
    p = float(stats.mannwhitneyu(story, abstract, alternative="less").pvalue)
    d = (abstract.mean() - story.mean()) / np.sqrt((abstract.var() + story.var()) / 2.0)
    reproduced = bool(story.mean() < abstract.mean() and p < 0.05)
    return {
        "effect_name": "effort_rating_story",
        "experiment": "exp0",
        "original_effect_size": PAPER_NA,
        "effect_size": d,
        "p": p,
        "reproduced": reproduced,
    }


EFFECTS = [check_model_based_stay, check_model_based_weight_story, check_effort_rating_story]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order."""
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
    print(f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'this':>10}  {'p':>8}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{r['p']:>8.4g}  {'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()
