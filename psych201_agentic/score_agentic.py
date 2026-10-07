"""Score the behavioral effects of the Psych-201-agentic papers on simulated (or human) data.

For every study with simulation CSVs of one agent in --sim_dir (files named
experiment=<study>_<exp>_agent=<agent>.csv, written by simulate_core.py), runs the effect
checks of the study's Hugging-Brain analysis.py (hf/<study>/analysis.py, fetched by
fetch_hf_scripts.py: an EFFECTS list of functions taking {exp: DataFrame} and returning
effect_name, experiment, original_effect_size, effect_size, reproduced) on those CSVs. An effect whose
experiment has no CSV is "no_data"; an effect that raises (e.g. a column the simulator does
not produce) is "error". --human scores the human data instead (hf/<study>/exp<i>.csv,
fetch_hf_scripts.py --with_csv), which is the reference every effect should reproduce on.
By default only the effects curated in experiments.json ("effects" of the selected
experiments) are reported; --all_effects reports every effect of every study with data.

Usage:
  python psych201_agentic/score_agentic.py --agent trained_<run>_temp0.7 [--json out.json] [--md out.md]
  python psych201_agentic/score_agentic.py --human [--study kool_2016_when ...]
"""
import argparse
import importlib.util
import json
import math
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
HF_DIR = os.path.join(HERE, "hf")
EXPERIMENTS_JSON = os.path.join(HERE, "experiments.json")
DEFAULT_SIM_DIR = os.path.join(HERE, "results_simulations")
DEFAULT_OUT_DIR = os.path.join(HERE, "results_effects")
FILE_RE = re.compile(r"^experiment=(?P<study>.+)_(?P<exp>exp\d+)_agent=(?P<agent>.+)\.csv$")
EXP_ONLY = re.compile(r"^exp\d+$")


def discover_csvs(sim_dir, agent):
    """{study: {exp: csv_path}} for the CSVs whose agent field equals `agent`."""
    found = {}
    for name in sorted(os.listdir(sim_dir)):
        m = FILE_RE.match(name)
        if m and m.group("agent") == agent:
            found.setdefault(m.group("study"), {})[m.group("exp")] = os.path.join(sim_dir, name)
    return found


def human_csvs(studies=None):
    """{study: {exp: csv_path}} for the human exp<i>.csv files present in hf/<study>/."""
    found = {}
    for study in sorted(os.listdir(HF_DIR)):
        if studies and study not in studies:
            continue
        for name in sorted(os.listdir(os.path.join(HF_DIR, study))):
            m = re.match(r"^(exp\d+)\.csv$", name)
            if m:
                found.setdefault(study, {})[m.group(1)] = os.path.join(HF_DIR, study, name)
    return found


def selected_effects():
    """{study: set of effect names} curated in experiments.json (union over the study's selected experiments)."""
    out = {}
    for x in json.load(open(EXPERIMENTS_JSON)):
        if x["selected"]:
            out.setdefault(x["study"], set()).update(x["effects"])
    return out


def load_analysis(study):
    path = os.path.join(HF_DIR, study, "analysis.py")
    if not os.path.exists(path):
        return None
    spec = importlib.util.spec_from_file_location(f"analysis_{study}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def score_study(study, csvs):
    """One row per effect of the study's analysis.py, run on the CSVs {exp: path}."""
    mod = load_analysis(study)
    if mod is None:
        return None
    effects = getattr(mod, "EFFECTS", None)
    if not effects:
        raise RuntimeError(f"{study}/analysis.py defines no EFFECTS list")
    data = {exp: pd.read_csv(path, low_memory=False) for exp, path in csvs.items()}
    rows = []
    for fn in effects:
        row = {"study": study, "effect_name": getattr(fn, "__name__", "?"), "experiment": None, "reproduced": False,
               "original_effect_size": None, "effect_size": None, "status": "ok", "error": None}
        try:
            r = fn(data)
        except KeyError as e:
            key = e.args[0] if e.args else None
            if isinstance(key, str) and EXP_ONLY.match(key) and key not in data:
                row.update(status="no_data", experiment=key)
            else:
                row.update(status="error", error=f"KeyError: {key!r}")
            rows.append(row)
            continue
        except Exception as e:  # noqa: BLE001 - one bad effect must not stop the rest
            row.update(status="error", error=f"{type(e).__name__}: {str(e)[:200]}")
            rows.append(row)
            continue
        for r_i in (r if isinstance(r, list) else [r]):  # a few effect functions return one dict per experiment
            if not isinstance(r_i, dict):
                rows.append({**row, "status": "error", "error": f"effect returned {type(r_i).__name__}, not a dict"})
                continue
            rows.append({**row, "effect_name": r_i.get("effect_name", row["effect_name"]),
                         "experiment": r_i.get("experiment"), "reproduced": bool(r_i.get("reproduced")),
                         "original_effect_size": _num(r_i.get("original_effect_size")),
                         "effect_size": _num(r_i.get("effect_size"))})
    return rows


def _num(x):
    if x is None:
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return str(x)


def _fmt(x):
    if x is None:
        return "n/a"
    if isinstance(x, str):
        return x
    return "nan" if math.isnan(x) else f"{x:+.3f}"


def markdown(payload):
    n, m = payload["n_reproduced"], payload["n_evaluated"]
    pct = f" ({100 * n / m:.0f}%)" if m else ""
    lines = [f"## Behavioral effects: {payload['agent']}", "",
             f"**{n} / {m} primary behavioral effects reproduced{pct}** on {payload['n_studies']} studies "
             f"(scored by `psych201_agentic/score_agentic.py`, effect checks from the Hugging-Brain `analysis.py` files).", "",
             "| study | effect | experiment | reproduced | paper | observed |", "|---|---|---|---|---:|---:|"]
    for r in payload["rows"]:
        verdict = {"ok": "YES" if r["reproduced"] else "NO", "no_data": "- (no data)"}.get(r["status"], "ERR")
        lines.append(f"| {r['study']} | {r['effect_name']} | {r['experiment'] or '-'} | {verdict} "
                     f"| {_fmt(r['original_effect_size'])} | {_fmt(r['effect_size'])} |")
    if payload["no_script"]:
        lines += ["", "Studies with data but no analysis.py: " + ", ".join(payload["no_script"]) + "."]
    if payload["study_errors"]:
        lines += ["", "Study-level errors: " + "; ".join(f"{s}: {e}" for s, e in payload["study_errors"]) + "."]
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--agent", default=None, help="agent field of the simulation CSVs, e.g. trained_<run>_temp0.7")
    ap.add_argument("--human", action="store_true", help="score the human hf/<study>/exp<i>.csv files instead")
    ap.add_argument("--study", nargs="*", default=None, help="restrict to these studies")
    ap.add_argument("--all_effects", action="store_true",
                    help="report every effect (default: only the effects curated in experiments.json)")
    ap.add_argument("--sim_dir", default=DEFAULT_SIM_DIR)
    ap.add_argument("--json", default=None, help=f"output json (default: {DEFAULT_OUT_DIR}/<agent>.json)")
    ap.add_argument("--md", default=None, help=f"output markdown (default: {DEFAULT_OUT_DIR}/<agent>.md)")
    args = ap.parse_args()
    if args.human == bool(args.agent):
        ap.error("give exactly one of --agent or --human")

    agent = "human" if args.human else args.agent
    found = human_csvs(args.study) if args.human else discover_csvs(args.sim_dir, args.agent)
    if args.study:
        found = {s: v for s, v in found.items() if s in args.study}
    curated = None if args.all_effects else selected_effects()
    if curated is not None:
        found = {s: v for s, v in found.items() if s in curated}
    print(f"Agent: {agent}\nMatched {sum(len(v) for v in found.values())} CSV(s) across {len(found)} studies"
          + (" (curated effects only; --all_effects for everything)." if curated is not None else "."))

    all_rows, no_script, study_errors = [], [], []
    for study in sorted(found):
        try:
            rows = score_study(study, found[study])
        except Exception as e:  # noqa: BLE001
            study_errors.append((study, f"{type(e).__name__}: {str(e)[:200]}"))
            print(f"\n=== {study} ===  ERROR: {e}")
            continue
        if rows is None:
            no_script.append(study)
            continue
        if curated is not None:  # errored effects carry the function name, matched via the "check_" prefix
            rows = [r for r in rows if r["effect_name"] in curated[study]
                    or r["effect_name"].removeprefix("check_") in curated[study]]
        all_rows.extend(rows)
        print(f"\n=== {study} ===  (data: {', '.join(sorted(found[study]))})")
        for r in rows:
            if r["status"] == "ok":
                verdict, tail = ("YES" if r["reproduced"] else "NO"), f"paper={_fmt(r['original_effect_size'])}  obs={_fmt(r['effect_size'])}"
            elif r["status"] == "no_data":
                verdict, tail = "--", f"no data for {r['experiment']}"
            else:
                verdict, tail = "ERR", r["error"]
            print(f"  {r['effect_name']:<46}{(r['experiment'] or ''):<12}{verdict:<5}{tail}")

    ok = [r for r in all_rows if r["status"] == "ok"]
    n_ok = sum(r["reproduced"] for r in ok)
    payload = {"agent": agent, "n_reproduced": int(n_ok), "n_evaluated": len(ok),
               "n_studies": len({r["study"] for r in ok}), "rows": all_rows, "no_script": no_script,
               "study_errors": study_errors}
    pct = f" ({100 * n_ok / len(ok):.0f}%)" if ok else ""
    print(f"\n{'=' * 72}\nTOTAL: {n_ok} / {len(ok)} primary behavioral effects reproduced{pct} by {agent} "
          f"on {payload['n_studies']} studies; {sum(r['status'] == 'no_data' for r in all_rows)} not evaluated (no data), "
          f"{sum(r['status'] == 'error' for r in all_rows)} errored.")
    for s, e in study_errors:
        print(f"  study failed: {s}: {e}")

    json_path = args.json or os.path.join(DEFAULT_OUT_DIR, f"{agent}.json")
    md_path = args.md or os.path.join(DEFAULT_OUT_DIR, f"{agent}.md")
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    os.makedirs(os.path.dirname(md_path), exist_ok=True)
    json.dump(payload, open(json_path, "w"), indent=1)
    open(md_path, "w").write(markdown(payload))
    print(f"Wrote {json_path} and {md_path}")


if __name__ == "__main__":
    main()
