# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "scipy", "statsmodels"]
# ///
"""Check the primary behavioral effects of Tessler & Franke (2018) against any dataset
in the Psych-301 unified schema (see schema.md).

Effects tested:
- ordering_asymmetry_exp1 (exp0): For lexical antonyms, antonym < neg_positive (full ordering);
  for morphological antonyms, antonym ≈ neg_positive (partial ordering). Tested as the
  interaction between antonym_type and the antonym vs neg_positive contrast (Helmert).
- ordering_asymmetry_exp2 (exp1, single-utterance): Same asymmetry replicated in Expt.2
  single-utterance conditions. Interaction between antonym_type and antonym vs neg_positive.
- context_interaction_morph (exp1, morphological): Context (single vs multiple) modulates
  the antonym vs neg_positive difference for morphological antonyms: bigger difference
  (more negative antonym) in multiple-utterance context.
"""
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols

EXPERIMENTS = ["exp0", "exp1"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def check_ordering_asymmetry_exp1(data: dict[str, pd.DataFrame]) -> dict:
    """In Expt. 1, lexical antonyms should show antonym < neg_positive
    (full ordering), while morphological antonyms should show antonym ≈ neg_positive
    (partial ordering). 
    Paper: 'the difference between the antonym vs. negated positive levels of adjective
    type interacted significantly with antonym type (morphological vs. lexical;
    b = 0.029, t(16) = 2.4, p = 0.029)' — p.1110, Results.
    """
    df = data["exp0"].copy()
    # Filter to antonym and neg_positive only
    sub = df[df["sentence_type"].isin(["antonym", "neg_positive"])].copy()
    
    # Compute per-participant mean difference (neg_positive - antonym) for each antonym type
    sub["is_neg_positive"] = (sub["sentence_type"] == "neg_positive").astype(int)
    
    diffs = sub.groupby(["participant_id", "negation"]).apply(
        lambda g: g[g["sentence_type"] == "neg_positive"]["response"].mean()
                 - g[g["sentence_type"] == "antonym"]["response"].mean()
    ).reset_index(name="diff")
    
    lex = diffs[diffs["negation"] == "lexical"]["diff"].dropna()
    morph = diffs[diffs["negation"] == "morphological"]["diff"].dropna()
    
    # Test: lexical diff > 0 (antonym < neg_positive)
    t_lex, p_lex = stats.ttest_1samp(lex, 0, alternative="greater")
    # Test: morphological diff ≈ 0 (no difference)
    t_morph, p_morph = stats.ttest_1samp(morph, 0, alternative="two-sided")
    
    # Interaction: paired t-test on participant-wise differences
    # Merge lexical and morphological diffs per participant
    merged = diffs.pivot(index="participant_id", columns="negation", values="diff").dropna()
    t_int, p_int = stats.ttest_rel(merged["lexical"], merged["morphological"], alternative="greater")
    
    lex_mean_diff = lex.mean()
    morph_mean_diff = morph.mean()
    
    # Paper's interaction b=0.029, t=2.4, p=0.029
    reproduced = (lex_mean_diff > 0.01) and (p_lex < 0.05) and (np.abs(morph_mean_diff) < 0.02) and (p_int < 0.05)
    
    return {
        "effect_name": "ordering_asymmetry_exp1",
        "experiment": "exp0",
        "original_effect_size": 0.029,
        "effect_size": float(lex_mean_diff - morph_mean_diff),
        "reproduced": bool(reproduced),
    }


def check_ordering_asymmetry_exp2(data: dict[str, pd.DataFrame]) -> dict:
    """In Expt. 2 single-utterance conditions, replicate the asymmetry:
    lexical antonyms distinguished from negated positives; morphological not.
    Paper: 'the interaction between the antonym vs. negated positive levels of
    adjective type and antonym type (morphological vs. lexical) was significant
    (b = 0.011, t(565) = 2.68, p = 0.0076)' — p.1111, Results.
    """
    df = data["exp1"].copy()
    sub = df[(df["utterance_type"] == "single")].copy()
    
    # Map adjective_type to categories
    def categorize(adj_type):
        if adj_type == "positive":
            return "positive"
        elif adj_type in ("lexant", "morphant"):
            return "antonym"
        elif adj_type in ("neg_lexant", "neg_morphant"):
            return "neg_antonym"
        elif adj_type == "neg_positive":
            return "neg_positive"
        return adj_type
    
    sub["cat"] = sub["adjective_type"].apply(categorize)
    
    # Focus on antonym vs neg_positive
    sub2 = sub[sub["cat"].isin(["antonym", "neg_positive"])].copy()
    
    # Per-participant means for each antonym_type × adjective_type combination
    means = sub2.groupby(["participant_id", "antonym_type_exp2", "cat"])["response"].mean().reset_index()
    
    # Compute difference (neg_positive - antonym) per participant
    pivot = means.pivot_table(index=["participant_id", "antonym_type_exp2"],
                               columns="cat", values="response").dropna()
    pivot["diff"] = pivot["neg_positive"] - pivot["antonym"]
    pivot = pivot.reset_index()
    
    lex = pivot[pivot["antonym_type_exp2"] == "lexical"]["diff"].dropna()
    morph = pivot[pivot["antonym_type_exp2"] == "morphological"]["diff"].dropna()
    
    t_lex, p_lex = stats.ttest_1samp(lex, 0, alternative="greater")
    t_morph, p_morph = stats.ttest_1samp(morph, 0, alternative="two-sided")
    t_int, p_int = stats.ttest_ind(lex, morph, alternative="greater")
    
    lex_mean_diff = lex.mean()
    morph_mean_diff = morph.mean()
    
    reproduced = (lex_mean_diff > 0.005) and (p_lex < 0.05) and (p_int < 0.05)
    
    return {
        "effect_name": "ordering_asymmetry_exp2",
        "experiment": "exp1",
        "original_effect_size": 0.011,
        "effect_size": float(lex_mean_diff - morph_mean_diff),
        "reproduced": bool(reproduced),
    }


def check_context_interaction_morph(data: dict[str, pd.DataFrame]) -> dict:
    """Context (single vs multiple utterances) modulates the antonym vs neg_positive
    difference for morphological antonyms.
    Paper: 'This interaction was also significant (b = 0.032, t(6457) = 6.73,
    p = 1.9e-11)' — p.1112, Results.
    """
    df = data["exp1"].copy()
    # Only morphological antonym conditions
    sub = df[df["antonym_type_exp2"] == "morphological"].copy()
    
    def categorize(adj_type):
        if adj_type == "positive":
            return "positive"
        elif adj_type == "morphant":
            return "antonym"
        elif adj_type == "neg_morphant":
            return "neg_antonym"
        elif adj_type == "neg_positive":
            return "neg_positive"
        return adj_type
    
    sub["cat"] = sub["adjective_type"].apply(categorize)
    sub2 = sub[sub["cat"].isin(["antonym", "neg_positive"])].copy()
    
    # For multiple utterance, each block has 4 sliders; the antonym/neg_positive
    # appear within the same block. Use block averaging.
    # For single utterance, each trial is a response.
    
    # Compute per-participant mean for each context × adjective combination
    means = sub2.groupby(["participant_id", "utterance_type", "cat"])["response"].mean().reset_index()
    
    # Compute difference per participant per context
    pivot = means.pivot_table(index=["participant_id", "utterance_type"],
                               columns="cat", values="response").dropna()
    pivot["diff"] = pivot["neg_positive"] - pivot["antonym"]
    pivot = pivot.reset_index()
    
    single = pivot[pivot["utterance_type"] == "single"]["diff"].dropna()
    multiple = pivot[pivot["utterance_type"] == "multiple"]["diff"].dropna()
    
    t_int, p_int = stats.ttest_ind(multiple, single, alternative="greater")
    
    single_mean = single.mean()
    multiple_mean = multiple.mean()
    
    # In multiple utterances, the difference should be bigger (antonym more negative
    # relative to neg_positive), i.e., diff_multiple > diff_single
    reproduced = (multiple_mean > single_mean) and (p_int < 0.05)
    
    return {
        "effect_name": "context_interaction_morph",
        "experiment": "exp1",
        "original_effect_size": 0.032,
        "effect_size": float(multiple_mean - single_mean),
        "reproduced": bool(reproduced),
    }


EFFECTS = [
    check_ordering_asymmetry_exp1,
    check_ordering_asymmetry_exp2,
    check_context_interaction_morph,
]


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