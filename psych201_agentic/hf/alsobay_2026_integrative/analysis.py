# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "statsmodels"]
# ///
"""Check the primary behavioral effects of Alsobay, Rand, Watts & Almaatouq
(2026, Science) 'Integrative experiments identify how punishment affects welfare
in public goods games' against a dataset in the Psych-301 unified schema.

NOTE: exp{N}.csv here contain only the punishment ("T") arm of each condition
(the transform dropped the paired control "C" arm), so the paper's headline
punishment-treatment-vs-control effect cannot be computed directly. The effects
below verify the two headline design factors the abstract names as the most
important in driving cooperation/welfare — communication and game length — by
their direct, within-available-data effect on per-round cooperation.

Effects tested:
- communication_increases_cooperation (exp0,exp1): chat (vs no chat) raises mean
  per-game contribution to the public fund; OLS on game-level mean contribution,
  expected positive sign and p < .05.
- game_length_increases_cooperation (exp0,exp1): longer games (numRounds above
  the wave median) raise mean per-game contribution; OLS on game-level mean
  contribution, expected positive sign and p < .05.
"""
from __future__ import annotations

import argparse

import pandas as pd
import statsmodels.formula.api as smf

EXPERIMENTS = ["exp0", "exp1"]


def load_data(sources: dict[str, str] | None = None) -> dict[str, pd.DataFrame]:
    """Returns {experiment_name: DataFrame}. Reads ./{exp}.csv unless --<exp> overrides."""
    sources = sources or {}
    return {exp: pd.read_csv(sources.get(exp, f"./{exp}.csv")) for exp in EXPERIMENTS}


def game_level(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per-round rows to game-level mean contribution plus each design factor."""
    g = (df.groupby(["gameId", "chat", "allOrNothing", "numRounds", "defaultContribProp",
                     "showOtherSummaries"])
         .agg(cont=("contribution", "mean")).reset_index())
    g["long"] = (g["numRounds"] > g["numRounds"].median()).astype(int)
    return g


def _ols_p(g, term):
    m = smf.ols(f"cont ~ {term}", data=g).fit()
    key = [k for k in m.params.index if k != "Intercept"][0]
    return float(m.params[key]), float(m.pvalues[key])


def check_communication_increases_cooperation(data: dict[str, pd.DataFrame]) -> dict:
    """"Communication emerges as the most important factor [determining welfare]" —
    Alsobay et al. 2026, Abstract."""
    g = pd.concat([game_level(data[e]) for e in ("exp0", "exp1")])
    beta, p = _ols_p(g, "C(chat)")
    return {
        "effect_name": "communication_increases_cooperation",
        "experiment": "exp0,exp1",
        "original_effect_size": 1.763,   # pooled chat OLS beta (learning+validation)
        "effect_size": beta,
        "reproduced": bool(beta > 0 and p < 0.05),
    }


def check_game_length_increases_cooperation(data: dict[str, pd.DataFrame]) -> dict:
    """"...followed by contribution framing, contribution type, game length, and
    outcome visibility" — Alsobay et al. 2026, Abstract (longer games support
    sustained cooperation in PGGs)."""
    g = pd.concat([game_level(data[e]) for e in ("exp0", "exp1")])
    beta, p = _ols_p(g, "C(long)")
    return {
        "effect_name": "game_length_increases_cooperation",
        "experiment": "exp0,exp1",
        "original_effect_size": 1.104,   # pooled long(>median numRounds) OLS beta
        "effect_size": beta,
        "reproduced": bool(beta > 0 and p < 0.05),
    }


EFFECTS = [check_communication_increases_cooperation,
           check_game_length_increases_cooperation]


def run_analysis(sources: dict[str, str] | None = None) -> list[dict]:
    """One result dict per effect in EFFECTS order. No printing."""
    data = load_data(sources)
    return [fn(data) for fn in EFFECTS]


def main() -> None:
    ap = argparse.ArgumentParser()
    for exp in EXPERIMENTS:
        ap.add_argument(f"--{exp}", default=None, help=f"CSV path for {exp}; defaults to ./{exp}.csv in CWD")
    args = ap.parse_args()
    sources = {exp: getattr(args, exp) for exp in EXPERIMENTS if getattr(args, exp)}
    for exp in EXPERIMENTS:
        print(f"{exp}: {sources.get(exp) or '(default — local ./' + exp + '.csv)'}")
    results = run_analysis(sources)
    w = max(len(r["effect_name"]) for r in results)
    print()
    print(f"{'effect':<{w}}  {'exp':<9}  {'orig':>10}  {'this':>10}  reproduced")
    for r in results:
        print(f"{r['effect_name']:<{w}}  {r['experiment']:<9}  "
              f"{r['original_effect_size']:>10.3f}  {r['effect_size']:>10.3f}  "
              f"{'YES' if r['reproduced'] else 'NO'}")


if __name__ == "__main__":
    main()