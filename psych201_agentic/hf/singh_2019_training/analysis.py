# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Singh et al. (2019) against any dataset
in the Psych-301 unified schema (see schema.md).

Effects tested:
- hit_rate_high_vs_low (exp0, exp1, exp2): Participants in the high-frequency (75%)
  condition have a higher hit rate at post-training than those in the low-frequency (25%)
  condition. Independent-samples t-test (one-tailed) on per-participant hit rates.
- fa_rate_high_vs_low (exp0, exp1, exp2): Participants in the high-frequency (75%)
  condition have a higher false-alarm rate at post-training than those in the low-frequency
  (25%) condition. Independent-samples t-test (one-tailed) on per-participant FA rates.
"""
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0", "exp1", "exp2"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _per_participant_rates(df: pd.DataFrame, high_label: str, low_label: str):
    """Return (hit_rates_high, hit_rates_low, fa_rates_high, fa_rates_low)."""
    phish = df[df["response_type"] == "phishing_decision"].copy()
    phish["response"] = phish["response"].astype(int)
    phish["is_phishing"] = phish["email_type"] == "phishing"
    phish["hit"] = (phish["is_phishing"]) & (phish["response"] == 1)
    phish["fa"] = (~phish["is_phishing"]) & (phish["response"] == 1)

    high = phish[phish["condition"] == high_label]
    low = phish[phish["condition"] == low_label]

    def _rates(sub):
        grp = sub.groupby("participant_id")
        hits = grp["hit"].sum()
        fas = grp["fa"].sum()
        n_phish = grp["is_phishing"].sum()
        n_ham = grp.size() - n_phish
        hr = (hits / n_phish).replace([np.inf, -np.inf], np.nan)
        far = (fas / n_ham).replace([np.inf, -np.inf], np.nan)
        return hr, far

    hr_h, far_h = _rates(high)
    hr_l, far_l = _rates(low)
    return hr_h, hr_l, far_h, far_l


def check_hit_rate_high_vs_low(data: dict[str, pd.DataFrame]) -> dict:
    """\"participants receiving higher frequency of phishing emails had a higher hit rate\" — Singh et al. 2019, Abstract."""
    results = {}
    exp_labels = {
        "exp0": ("75_OutFeed", "25_OutFeed"),
        "exp1": ("75_Inc", "25_Inc"),
        "exp2": ("75_DetFeed", "25_DetFeed"),
    }
    for exp in EXPERIMENTS:
        df = data[exp]
        df_pt = df[df["phase"] == "post_training"]
        high_label, low_label = exp_labels[exp]
        hr_h, hr_l, _, _ = _per_participant_rates(df_pt, high_label, low_label)
        common = hr_h.index.intersection(hr_l.index)
        t_stat, p_val = stats.ttest_ind(hr_h.dropna(), hr_l.dropna(), alternative="greater")
        orig_es = None  # Paper does not report exact t values in accessible part
        reproduced = bool(t_stat > 0 and p_val < 0.05)
        results[exp] = {
            "effect_name": "hit_rate_high_vs_low",
            "experiment": exp,
            "original_effect_size": float("nan"),
            "effect_size": float(t_stat),
            "p_value": float(p_val),
            "reproduced": reproduced,
        }
    return results


def check_fa_rate_high_vs_low(data: dict[str, pd.DataFrame]) -> dict:
    """\"participants receiving higher frequency of phishing emails had a higher ... false alarm rate\" — Singh et al. 2019, Abstract."""
    results = {}
    exp_labels = {
        "exp0": ("75_OutFeed", "25_OutFeed"),
        "exp1": ("75_Inc", "25_Inc"),
        "exp2": ("75_DetFeed", "25_DetFeed"),
    }
    for exp in EXPERIMENTS:
        df = data[exp]
        df_pt = df[df["phase"] == "post_training"]
        high_label, low_label = exp_labels[exp]
        _, _, far_h, far_l = _per_participant_rates(df_pt, high_label, low_label)
        t_stat, p_val = stats.ttest_ind(far_h.dropna(), far_l.dropna(), alternative="greater")
        reproduced = bool(t_stat > 0 and p_val < 0.05)
        results[exp] = {
            "effect_name": "fa_rate_high_vs_low",
            "experiment": exp,
            "original_effect_size": float("nan"),
            "effect_size": float(t_stat),
            "p_value": float(p_val),
            "reproduced": reproduced,
        }
    return results


EFFECTS = [check_hit_rate_high_vs_low, check_fa_rate_high_vs_low]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    data = load_data(sources)
    results = []
    for fn in EFFECTS:
        res = fn(data)
        if isinstance(res, dict):
            results.append(res)
        else:
            results.extend(res)
    # Flatten multi-experiment dicts into list of individual results
    flat = []
    for r in results:
        if isinstance(r, dict) and all(k in r for k in ("effect_name", "experiment")):
            flat.append(r)
        else:
            for exp_r in r.values():
                flat.append(exp_r)
    return flat


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
    print(f"{'effect':<{w}}  {'exp':<4}  {'orig':>10}  {'t':>10}  {'p':>8}  reproduced")
    for r in results:
        orig = r.get("original_effect_size", float("nan"))
        es = r.get("effect_size", float("nan"))
        pv = r.get("p_value", float("nan"))
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<4}  "
              f"{orig if not np.isnan(orig) else 'N/A':>10}  {es:>10.3f}  {pv:>8.4f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()