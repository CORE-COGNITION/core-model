# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "scipy"]
# ///
"""Check the primary behavioral effects of Cox, Hemmer, Aue, & Criss (2018),
"Information and Processes Underlying Semantic and Episodic Memory Across Tasks,
Items, and Individuals", JEP:General, against any dataset in the Psych-301
unified schema (see schema.md).

Effects tested:
- above_chance_recognition (exp0): in the three binary-choice tasks (lexical
  decision, single-item recognition, associative recognition) the 'YES' rate to
  targets (hit rate) exceeds the 'YES' rate to foils (false-alarm rate); paired
  per-participant t-test, expected positive. Memory well above chance.
- cued_recall_above_chance (exp0): among the responses a participant produces in
  cued recall, the proportion that is the correct studied target exceeds chance
  (0.5) relative to producing a nontarget intrusion; one-sample t-test per
  participant, expected above 0.5.
- free_recall_above_chance (exp0): among the words a participant produces in free
  recall, the proportion that is a studied item (correct or prior/intra-list
  studied word) exceeds the proportion of non-studied extralist words (chance 0.5);
  one-sample t-test per participant, expected above 0.5.
"""
from __future__ import annotations

import argparse
import numpy as np
import pandas as pd
from scipy import stats

EXPERIMENTS = ["exp0"]

BINARY_TASKS = [3, 4, 0]  # lexical decision, single recognition, associative recognition
CR_TASK = 1
FR_TASK = 2


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}."""
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def _test_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["phase"] == "test"]


def check_above_chance_recognition(data: dict[str, pd.DataFrame]) -> dict:
    """"
    For binary choice tasks ... 'Targets' and 'foils' are defined as words and
    pseudowords in lexical decision, studied and unstudied words in single
    recognition, and intact and rearranged pairs in associative recognition ...
    (Figure 3 caption) — Cox et al. 2018, p.555, Results / Figure 3.
    """
    df = _test_rows(data["exp0"])
    sub = df[df["task_id"].isin(BINARY_TASKS)]
    rows = []
    for pid, g in sub.groupby("participant_id"):
        h = int((g["resp.type"] == "Hit").sum())
        m = int((g["resp.type"] == "Miss").sum())
        fa = int((g["resp.type"] == "FA").sum())
        cr = int((g["resp.type"] == "CR").sum())
        hr = h / (h + m) if (h + m) else np.nan
        far = fa / (fa + cr) if (fa + cr) else np.nan
        rows.append((pid, hr, far))
    d = pd.DataFrame(rows, columns=["pid", "hr", "far"]).dropna()
    diff = d["hr"] - d["far"]
    tstat, p = stats.ttest_rel(d["hr"], d["far"])
    effect = float(diff.mean())
    reproduced = bool(diff.mean() > 0 and p < 0.05)
    return {
        "effect_name": "above_chance_recognition",
        "experiment": "exp0",
        "original_effect_size": 0.60,
        "effect_size": effect,
        "t": float(tstat),
        "p": float(p),
        "n": int(len(d)),
        "reproduced": reproduced,
    }


def _cued_recall_correct(data: dict[str, pd.DataFrame]) -> pd.Series:
    df = _test_rows(data["exp0"])
    sub = df[df["task_id"] == CR_TASK]
    produced = sub[sub["recall.type"].notna()]
    res = {}
    for pid, g in produced.groupby("participant_id"):
        n = len(g)
        if n == 0:
            continue
        res[pid] = int((g["recall.type"] == "Correct").sum()) / n
    return pd.Series(res).dropna()


def check_cued_recall_above_chance(data: dict[str, pd.DataFrame]) -> dict:
    """"
    For cued recall, response probability is the probability of producing a
    response that is either the target item (correct recall) or a nontarget/foil
    item (intrusion) (Figure 3 caption) — Cox et al. 2018, p.555, Results / Fig. 3.
    """
    d = _cued_recall_correct(data)
    tstat, p = stats.ttest_1samp(d, 0.5)
    effect = float(d.mean())
    reproduced = bool(d.mean() > 0.5 and p < 0.05)
    return {
        "effect_name": "cued_recall_above_chance",
        "experiment": "exp0",
        "original_effect_size": 0.70,
        "effect_size": effect,
        "t": float(tstat),
        "p": float(p),
        "n": int(len(d)),
        "reproduced": reproduced,
    }


def _free_recall_studied(data: dict[str, pd.DataFrame]) -> pd.Series:
    df = _test_rows(data["exp0"])
    sub = df[df["task_id"] == FR_TASK]
    produced = sub[sub["recall.type"].notna()]
    res = {}
    for pid, g in produced.groupby("participant_id"):
        n = len(g)
        if n == 0:
            continue
        studied = int((g["recall.type"] != "Extralist intrusion").sum())
        res[pid] = studied / n
    return pd.Series(res).dropna()


def check_free_recall_above_chance(data: dict[str, pd.DataFrame]) -> dict:
    """"
    For free recall, response probability is the proportion out of 40 possible
    responses that are correct studied (target) items or nontarget/foil items
    (intrusions) (Figure 3 caption) — Cox et al. 2018, p.555, Results / Fig. 3.
    Produced words are predominantly studied items rather than non-studied foils.
    """
    d = _free_recall_studied(data)
    tstat, p = stats.ttest_1samp(d, 0.5)
    effect = float(d.mean())
    reproduced = bool(d.mean() > 0.5 and p < 0.05)
    return {
        "effect_name": "free_recall_above_chance",
        "experiment": "exp0",
        "original_effect_size": 0.70,
        "effect_size": effect,
        "t": float(tstat),
        "p": float(p),
        "n": int(len(d)),
        "reproduced": reproduced,
    }


EFFECTS = [check_above_chance_recognition, check_cued_recall_above_chance,
           check_free_recall_above_chance]


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
