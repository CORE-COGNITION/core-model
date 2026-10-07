# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Evangelidis, Levav & Simonson (2023),
"The Upscaling Effect" (JCR), against any dataset in the Psych-301 unified schema.

Effects tested:
- upscaling_basic_study1 (exp0): between-subject; adding a symmetrically dominated
  decoy (three_options vs two_options) increases choice share of the HD option
  (response==1), tested with a logistic regression (positive logit coefficient, p<.05).
- upscaling_within_study2 (exp1): within-subject; each participant chooses twice
  (trial 0 = two-option, trial 1 = three-option). The decoy shifts choice toward the
  HD option: more participants switch HF->HD than HD->HF (McNemar/binomial, p<.05).
- hd_justifiability_study5fu (exp5): follow-up rating task (response 1..7). The HD
  option is rated as easier to justify when its price is low than when high
  (independent-samples t-test, positive difference, p<.05).
"""
from __future__ import annotations

import argparse
import pandas as pd
from scipy import stats
from statsmodels.formula.api import logit

EXPERIMENTS = ["exp0", "exp1", "exp5"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}.

    sources: optional {experiment_name: csv_path} override. With no overrides,
    loads ./{exp}.csv from CWD.

    Required columns per experiment:
      exp0: participant_id, trial, response, condition
      exp1: participant_id, trial, response
      exp5: participant_id, trial, version, option, hd_price, response
    """
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def check_upscaling_basic_study1(data: dict[str, pd.DataFrame]) -> dict:
    """\"Overall, we found strong support for the upscaling effect (table 1). Participants
    were significantly more likely to select the HD option when the symmetrically dominated
    decoy was added to the choice set compared to the control two-option condition (53.1% vs.
    33.9%; Wald chi2 = 74.33, p < .001; logit d = 0.44).\" — Evangelidis et al., 2023, p.497,
    Study 1 Results and Discussion. HD = response 1 (option B); decoy present = three_options."""
    df = data["exp0"].copy()
    df["is_HD"] = (df["response"] == 1).astype(int)
    model = logit("is_HD ~ C(condition, Treatment(reference='two_options'))", df).fit(disp=0)
    coef = float(model.params.iloc[1])
    p = float(model.pvalues.iloc[1])
    share_two = (df.loc[df.condition == "two_options", "response"] == 1).mean()
    share_three = (df.loc[df.condition == "three_options", "response"] == 1).mean()
    reproduced = bool(coef > 0 and p < 0.05)
    return {
        "effect_name": "upscaling_basic_study1",
        "experiment": "exp0",
        "original_effect_size": 0.44,
        "effect_size": coef,
        "reproduced": reproduced,
        "hd_share_two": float(share_two),
        "hd_share_three": float(share_three),
        "p": round(p, 6),
    }


def check_upscaling_within_study2(data: dict[str, pd.DataFrame]) -> dict:
    """\"...whereas 18.9% of the participants who initially selected the HF option (brand A)
    switched to the HD option (brand B), only 3.6% of those who first selected the HD option
    (brand B) switched to the HF option (brand A), Wald chi2 = 19.28, p < .001.\" — Evangelidis
    et al., 2023, p.499, Study 2 Results. Response 1 = HD (brand B, 4TB). Within-subject: trial 0
    is the two-option initial choice, trial 1 the three-option choice with decoy."""
    df = data["exp1"].copy()
    df["trial"] = df["trial"].astype(int)
    t0 = df[df.trial == 0].set_index("participant_id")["response"]
    t1 = df[df.trial == 1].set_index("participant_id")["response"]
    keep = t0.isin([0, 1]) & t1.isin([0, 1])
    a, b = t0[keep], t1[keep]
    hf_to_hd = int(((a == 0) & (b == 1)).sum())
    hd_to_hf = int(((a == 1) & (b == 0)).sum())
    p = stats.binomtest(hf_to_hd, hf_to_hd + hd_to_hf).pvalue
    share0 = float((t0 == 1).mean())
    share1 = float((t1 == 1).mean())
    reproduced = bool(hf_to_hd > hd_to_hf and p < 0.05)
    return {
        "effect_name": "upscaling_within_study2",
        "experiment": "exp1",
        "original_effect_size": 1.01,
        "effect_size": hf_to_hd - hd_to_hf,
        "reproduced": reproduced,
        "hf_to_hd": hf_to_hd,
        "hd_to_hf": hd_to_hf,
        "hd_share_two": share0,
        "hd_share_three": share1,
        "p": round(float(p), 6),
    }


def check_hd_justifiability_study5fu(data: dict[str, pd.DataFrame]) -> dict:
    """\"Participants felt that it was easier to justify choosing the HD option when the price
    of the HD option was low (M = 6.12, SD = 1.16) compared to high (M = 5.27, SD = 1.47;
    t(300) = 5.55, p < .001).\" — Evangelidis et al., 2023, p.503, Study 5 Follow-up. HD option:
    version v1 -> option B; version v2 -> option A (4TB, high-capacity hard drive)."""
    df = data["exp5"].copy()
    df["is_HD"] = ((df["version"] == "v1") & (df["option"] == "B")) | (
        (df["version"] == "v2") & (df["option"] == "A")
    )
    hd = df[df["is_HD"]]
    lo = hd.loc[hd["hd_price"] == "low", "response"]
    hi = hd.loc[hd["hd_price"] == "high", "response"]
    t, p = stats.ttest_ind(lo, hi)
    reproduced = bool(float(lo.mean()) > float(hi.mean()) and p < 0.05)
    return {
        "effect_name": "hd_justifiability_study5fu",
        "experiment": "exp5",
        "original_effect_size": 0.64,
        "effect_size": float(lo.mean() - hi.mean()),
        "reproduced": reproduced,
        "mean_low": float(lo.mean()),
        "mean_high": float(hi.mean()),
        "p": round(float(p), 6),
    }


EFFECTS = [check_upscaling_basic_study1, check_upscaling_within_study2, check_hd_justifiability_study5fu]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. No printing — pure return value."""
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
