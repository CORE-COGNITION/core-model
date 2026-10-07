# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Jansen, Rafferty & Griffiths (2021),
"A rational model of the Dunning-Kruger effect supports insensitivity to evidence
in low performers" (Nature Human Behaviour 5, 756-763) against any dataset in the
Psych-301 unified schema (see schema.md).

Two studies (~4,000 participants each) replicate the seminal Dunning-Kruger design:
participants answer 20 grammar (exp0) or 20 logical-reasoning/LSAT (exp1) five-option
questions and, before and after the test, estimate how many of the 20 they will / did
answer correctly. "All analyses in this paper are based solely on the absolute ratings
of performance made after the test" (Methods, p. 8): the post-test estimate `absAssess1`
(0-20) against the actual score `SC0` (0-20, the Qualtrics number correct).

Effects tested, per experiment (Results, pp. 5-6):
- estimated_score_exceeds_actual: the mean post-test estimated score is above the mean
  actual score (grammar 12.49 vs 10.17; logical reasoning 10.86 vs 9.45), paired
  t-test p < .05. Original effect size = the reported mean difference.
- lowest_quartile_overestimates_most: grouping participants by quartile of actual score
  (Fig. 5b / 6b; "considerable overconfidence by the worst performers"), the bottom
  quartile's mean (estimated - actual) is positive and larger than the top quartile's.
  The paper gives this gap only graphically, so the original effect size is NaN.
- quadratic_beats_linear: a quadratic regression of estimated score on actual score
  fits better than a linear one (nested-model F test; grammar F = 34.25, logical
  reasoning F = 56.87, both P < 0.001), p < .05. Original effect size = the reported F.

The paper's numbers come from its post-exclusion samples (3,515 / 3,543 participants).
This script runs on every participant in expN.csv with both values present (the
no-exclusions source; the paper states that without exclusions "results are
substantially the same"), so the sizes differ while the effects must hold.
"""
from __future__ import annotations

import argparse
import pandas as pd
import numpy as np
from scipy import stats

EXPERIMENTS = ["exp0", "exp1"]

# paper, Results pp. 5-6: mean estimated score minus mean actual score; quadratic-vs-linear F
ORIGINAL_MEAN_DIFF = {"exp0": 12.49 - 10.17, "exp1": 10.86 - 9.45}
ORIGINAL_F = {"exp0": 34.25, "exp1": 56.87}


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD -- cd into a checkout of the dataset repo before
    running.

    Required columns per experiment (exp0 and exp1 alike): participant_id, SC0, absAssess1
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _paired(df: pd.DataFrame) -> pd.DataFrame:
    """Per-participant frame with the actual score and the post-test estimate.

    `SC0` is the Qualtrics score: the number of the 20 questions answered correctly
    (0..20), constant across the participant's rows. `absAssess1` is the post-test
    answer to "How many of the 20 questions ... do you think you answered correctly?"
    (0..20). Participants missing either value (drop-outs) are excluded.
    """
    g = (
        df.groupby("participant_id", as_index=False)
        .agg(score=("SC0", "first"), estimated=("absAssess1", "first"))
    )
    return g.dropna(subset=["score", "estimated"])


def check_estimated_score_exceeds_actual(data: dict[str, pd.DataFrame], exp: str) -> dict:
    """"the mean estimated score was 12.49 (s.d. = 3.91)" against "participants scored
    10.17 out of 20 (s.d. = 3.40)" (grammar); 10.86 against 9.45 (logical reasoning) --
    Jansen et al., 2021, Results pp. 5-6. Reproduced when the mean post-test estimate
    exceeds the mean actual score with a paired t-test p < .05."""
    g = _paired(data[exp])
    diff = g["estimated"] - g["score"]
    _, p = stats.ttest_rel(g["estimated"], g["score"])
    return {
        "effect_name": "estimated_score_exceeds_actual",
        "experiment": exp,
        "original_effect_size": ORIGINAL_MEAN_DIFF[exp],
        "effect_size": float(diff.mean()),
        "reproduced": bool(diff.mean() > 0 and p < 0.05),
    }


def check_lowest_quartile_overestimates_most(data: dict[str, pd.DataFrame], exp: str) -> dict:
    """"The overconfidence of the lowest-scoring participants appeared substantial"
    (grammar, p. 5); "considerable overconfidence by the worst performers" (logical
    reasoning, p. 5); Fig. 5b / 6b group participants by quartile of score as in the
    original Kruger & Dunning analysis. Reproduced when the bottom score quartile's mean
    (estimated - actual) is positive and larger than the top quartile's. The paper
    reports the gap only graphically (original_effect_size NaN)."""
    g = _paired(data[exp])
    g["over"] = g["estimated"] - g["score"]
    g["q"] = pd.qcut(g["score"], 4, labels=False, duplicates="drop")
    bottom = g.loc[g["q"] == g["q"].min(), "over"].mean()
    top = g.loc[g["q"] == g["q"].max(), "over"].mean()
    return {
        "effect_name": "lowest_quartile_overestimates_most",
        "experiment": exp,
        "original_effect_size": float("nan"),
        "effect_size": float(bottom - top),
        "reproduced": bool(bottom > 0 and bottom > top),
    }


def check_quadratic_beats_linear(data: dict[str, pd.DataFrame], exp: str) -> dict:
    """"we additionally fit linear and quadratic models to the data, finding that the
    quadratic model provided a better fit compared with the linear model (F = 34.25,
    P < 0.001)" (grammar, p. 5); "(F = 56.87, P < 0.001)" (logical reasoning, p. 6).
    Nested-model F test of estimated ~ score + score^2 against estimated ~ score, as in
    the paper's analysis notebooks (anova(model1, model0)). Reproduced when p < .05."""
    g = _paired(data[exp])
    x = g["score"].to_numpy(dtype=float)
    y = g["estimated"].to_numpy(dtype=float)
    n = len(y)
    x_lin = np.column_stack([np.ones(n), x])
    x_quad = np.column_stack([np.ones(n), x, x ** 2])
    sse_lin = float(((y - x_lin @ np.linalg.lstsq(x_lin, y, rcond=None)[0]) ** 2).sum())
    sse_quad = float(((y - x_quad @ np.linalg.lstsq(x_quad, y, rcond=None)[0]) ** 2).sum())
    f_stat = ((sse_lin - sse_quad) / 1.0) / (sse_quad / (n - 3))
    p = float(stats.f.sf(f_stat, 1, n - 3))
    return {
        "effect_name": "quadratic_beats_linear",
        "experiment": exp,
        "original_effect_size": ORIGINAL_F[exp],
        "effect_size": float(f_stat),
        "reproduced": bool(p < 0.05),
    }


EFFECTS = [
    check_estimated_score_exceeds_actual,
    check_lowest_quartile_overestimates_most,
    check_quadratic_beats_linear,
]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per (effect, experiment), effects in EFFECTS order and experiments
    in EXPERIMENTS order. No printing -- pure return value."""
    data = load_data(sources)
    return [fn(data, exp) for fn in EFFECTS for exp in EXPERIMENTS]


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
            print(f"{exp}: (default -- local ./{exp}.csv)")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<8}  {'orig':>10}  {'this':>10}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<8}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()
