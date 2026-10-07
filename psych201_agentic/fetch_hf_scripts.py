"""Fetch the simulators and analysis scripts of the Psych-201-agentic sources.

For every dataset included in manifest.json (pinned commit), downloads from the
Hugging-Brain repo, verbatim and read-only, into hf/<study>/:
  simulate<i>.py   text simulator of experiment i (for every transcripts<i>.jsonl with presses, where present)
  analysis.py      effect checks of the paper (EFFECTS list, run_analysis(sources))
  README.md        dataset card (its "## Experiment summary" is shown by results_browser/build.py)
  exp<i>.csv       the human trial-level data (only with --with_csv [study ...]; 2.9 GB for all, gitignored;
                   olschewski_2025_optimal's simulators read theirs, 21 MB)
and writes experiments.json: one entry per experiment that has a simulator
(index, study, exp, simulator path, task class, participants and choices from
data/build_log.json, stripped = non-letter responses in the source transcript).
The hand-curated selection fields of an existing experiments.json (selected, effects,
note; see README "Selection") are carried over by (study, exp).

Usage:
    python psych201_agentic/fetch_hf_scripts.py [--with_csv [study ...]]
"""
import argparse
import importlib.util
import inspect
import json
import os
import re

from huggingface_hub import HfApi, hf_hub_download

HERE = os.path.dirname(os.path.abspath(__file__))
HF_DIR = os.path.join(HERE, "hf")
TRANSCRIPT = re.compile(r"^transcripts(\d+)\.jsonl$")


def task_class(path):
    """Name of the simulator's task class: the one class defined in the module with a `simulate` method."""
    spec = importlib.util.spec_from_file_location("_sim_" + os.path.basename(os.path.dirname(path)), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    classes = [n for n, c in inspect.getmembers(mod, inspect.isclass)
               if c.__module__ == mod.__name__ and callable(getattr(c, "simulate", None))]
    assert len(classes) == 1, f"{path}: expected one task class, found {classes}"
    return classes[0]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--with_csv", nargs="*", default=None, metavar="STUDY",
                   help="also download the human exp<i>.csv files (of these studies; all if none given)")
    args = p.parse_args()
    entries = [e for e in json.load(open(os.path.join(HERE, "manifest.json"))) if e["included"]]
    exp_path = os.path.join(HERE, "experiments.json")
    previous = {(x["study"], x["exp"]): x for x in json.load(open(exp_path))} if os.path.exists(exp_path) else {}
    build_log = json.load(open(os.path.join(HERE, "data", "build_log.json")))["studies"]
    api = HfApi()

    experiments = []
    for e in sorted(entries, key=lambda e: e["id"]):
        study = e["id"].split("/")[1]
        files = set(api.list_repo_files(e["id"], repo_type="dataset", revision=e["sha"]))
        wanted = ["analysis.py", "README.md"]
        for t in e["transcripts"]:
            if build_log[study]["experiments"][t].get("rows_kept", 0) == 0:
                continue  # no letter presses in the transcript: not in the dataset, nothing to simulate
            i = int(TRANSCRIPT.match(t).group(1))
            with_csv = args.with_csv is not None and (not args.with_csv or study in args.with_csv)
            wanted += [f"simulate{i}.py"] + ([f"exp{i}.csv"] if with_csv else [])
        missing = [f for f in wanted if f not in files]
        for f in wanted:
            if f in files:
                hf_hub_download(e["id"], f, repo_type="dataset", revision=e["sha"], local_dir=os.path.join(HF_DIR, study))
        print(f"{study:40s} {len(wanted) - len(missing)} files" + (f"  missing: {missing}" if missing else ""), flush=True)

        for t in e["transcripts"]:
            i = int(TRANSCRIPT.match(t).group(1))
            sim = f"simulate{i}.py"
            log = build_log[study]["experiments"][t]
            if sim not in files or log.get("rows_kept", 0) == 0:
                continue
            prev = previous.get((study, f"exp{i}"), {})
            experiments.append({
                "study": study, "exp": f"exp{i}", "hf_id": e["id"], "sha": e["sha"],
                "simulator": f"hf/{study}/{sim}", "task_class": task_class(os.path.join(HF_DIR, study, sim)),
                "analysis": f"hf/{study}/analysis.py",
                "participants": log["rows_kept"], "choices": log["choices"], "stripped": log.get("stripped", 0),
                "selected": prev.get("selected", False), "effects": prev.get("effects", []),
                "note": prev.get("note", "" if prev else "new experiment: not yet reviewed for selection"),
            })
    for k, x in enumerate(experiments):
        x = {"index": k, **x}
        experiments[k] = x
    json.dump(experiments, open(exp_path, "w"), indent=1)
    print(f"\n{len(experiments)} experiments with a simulator -> experiments.json")


if __name__ == "__main__":
    main()
