"""Build Psych-201-agentic: the Hugging-Brain psych-301 collections as a
Psych-201-discrete-style train/test dataset.

Sources: every dataset in the collections listed in COLLECTIONS that carries a
`psych-101` or `psych-201` tag and has `transcripts<i>.jsonl` files (one file
per experiment, one row per participant; responses are wrapped as
`[HUMAN_RESPONSE]X[/HUMAN_RESPONSE]`), minus EXCLUDE. The `verification:<pass|needs-review>`
tag of the Hub's auto-exp-verify pass is recorded in the manifest, not filtered on
(needs-review datasets are included on purpose).

Transform (the discrete transform of Psych-201-discrete, with the source markers kept):
  * a response that is a single uppercase letter keeps its `[HUMAN_RESPONSE]X[/HUMAN_RESPONSE]` markers (button press);
  * any other response keeps its text and loses the markers;
  * a row without any letter response left is dropped.
The markers are single tokens of utils.build_tokenizer and utils.load_data rewrites X to PRESS_X. (Until 2026-09-16 the
build wrote ` <<X>>` like Psych-201-discrete, inserting a missing space before `<<` and defusing stray `<<` / `>>`.)

Split (mirrors Psych-201-discrete): per study (= Hugging-Brain dataset), rows are
shuffled with a fixed seed and min(100, floor(0.1 * n_rows)) go to the test set;
sampling is at row level (a participant with several experiments can be in both).

Outputs (data/ is gitignored):
  data/raw/<study>/transcripts<i>.jsonl   downloaded sources (pinned to the commit in manifest.json)
  data/train.jsonl, data/test.jsonl       columns: text, study, experiment, participant,
                                           is_psych101, is_psych201, n_choices, meta (json string of the other source fields)
  data/build_log.json                      per-study / per-experiment counts
  manifest.json                            every dataset of the collections: tags, commit, files, included or why not

Usage:
    python psych201_agentic/build_dataset.py [--seed 0] [--skip_download]
"""
import argparse
import json
import math
import os
import re
from collections import Counter

import numpy as np
from huggingface_hub import HfApi, hf_hub_download

HERE = os.path.dirname(os.path.abspath(__file__))
COLLECTIONS = [
    "Hugging-Brain/psych-301-pass",
    "Hugging-Brain/psych-301-needs-review",
    "Hugging-Brain/psych-301-fail",
]
TAGS = {"psych-101", "psych-201"}
# datasets excluded although tagged (id -> reason)
EXCLUDE = {
    "Hugging-Brain/pedroni_2017_risk": "same Basel-Berlin Risk Study sessions as frey_2017_risk (same 1507 participants, "
    "same tasks and choices, concatenated into one transcript); kept once to avoid train/test leakage",
    "Hugging-Brain/xiong_2023_neural": "33 rows of ~440k chars (~438k phoneme tokens), longer than the 304,500-token "
    "training pack; excluded here since 2026-09-15 (before: dropped at load time by utils.AGENTIC_EXCLUDE_STUDIES)",
}
OPEN, CLOSE = "[HUMAN_RESPONSE]", "[/HUMAN_RESPONSE]"
RESP = re.compile(r"\[HUMAN_RESPONSE\](.*?)\[/HUMAN_RESPONSE\]", re.S)
LETTER = re.compile(r"[A-Z]")
TRANSCRIPT = re.compile(r"^transcripts(\d+)\.jsonl$")
CORE_FIELDS = ("text", "paper", "experiment", "participant")


def list_collections(api):
    """One manifest entry per dataset of the collections (tags, commit, transcript files, note)."""
    entries = []
    for slug in COLLECTIONS:
        col = api.get_collection(slug)
        for item in col.items:
            if item.item_type != "dataset":
                continue
            info = api.dataset_info(item.item_id)
            files = sorted(s.rfilename for s in info.siblings if TRANSCRIPT.match(s.rfilename))
            entries.append({
                "id": item.item_id,
                "collection": slug.split("/")[1],
                "note": (item.note or ""),
                "tags": sorted(t for t in info.tags if t.startswith(("psych-", "text-format", "paradigm", "verification"))),
                "sha": info.sha,
                "transcripts": files,
            })
    return entries


def select(entries):
    for e in entries:
        tagged = bool(TAGS & set(e["tags"]))
        if not tagged:
            e["included"], e["reason"] = False, "no psych-101/psych-201 tag"
        elif e["id"] in EXCLUDE:
            e["included"], e["reason"] = False, EXCLUDE[e["id"]]
        elif not e["transcripts"]:
            e["included"], e["reason"] = False, "no transcripts jsonl"
        else:
            e["included"], e["reason"] = True, ""
    return [e for e in entries if e["included"]]


def download(entry, raw_dir):
    name = entry["id"].split("/")[1]
    paths = []
    for f in entry["transcripts"]:
        paths.append(hf_hub_download(entry["id"], f, repo_type="dataset", revision=entry["sha"],
                                     local_dir=os.path.join(raw_dir, name)))
    return paths


def to_discrete(text):
    """Letter responses keep their `[HUMAN_RESPONSE]X[/HUMAN_RESPONSE]` markers, other responses lose them.
    Returns (text, n_letters, n_other, n_stray): stray = marker strings left outside letter responses (0 in every source)."""
    n_letter = n_other = 0

    def sub(m):
        nonlocal n_letter, n_other
        inner = m.group(1)
        if LETTER.fullmatch(inner):
            n_letter += 1
            return m.group(0)
        n_other += 1
        return inner

    out = RESP.sub(sub, text)
    n_stray = out.count(OPEN) + out.count(CLOSE) - 2 * n_letter
    return out, n_letter, n_other, n_stray


def load_study(entry, raw_dir):
    """All rows of one study after the discrete transform (dropped rows counted, not returned)."""
    name = entry["id"].split("/")[1]
    is101, is201 = "psych-101" in entry["tags"], "psych-201" in entry["tags"]
    rows, log = [], {"experiments": {}, "rows_raw": 0, "rows_kept": 0, "choices": 0, "stripped": 0, "stray_markers": 0}
    for f in sorted(entry["transcripts"], key=lambda s: int(TRANSCRIPT.match(s).group(1))):
        exp_log = Counter()
        with open(os.path.join(raw_dir, name, f)) as fh:
            for line in fh:
                r = json.loads(line)
                exp_log["rows_raw"] += 1
                text, n_letter, n_other, n_stray = to_discrete(r["text"])
                exp_log["stripped"] += n_other
                exp_log["stray_markers"] += n_stray
                if n_letter == 0:
                    continue
                exp_log["rows_kept"] += 1
                exp_log["choices"] += n_letter
                rows.append({
                    "text": text,
                    "study": name,
                    "experiment": f"{name}/{r['experiment']}",
                    "participant": str(r["participant"]),
                    "is_psych101": is101,
                    "is_psych201": is201,
                    "n_choices": n_letter,
                    "meta": json.dumps({k: v for k, v in r.items() if k not in CORE_FIELDS}, default=str),
                })
        log["experiments"][f] = dict(exp_log)
        for k in log:
            if k != "experiments":
                log[k] += exp_log[k]
    return rows, log


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--skip_download", action="store_true", help="reuse data/raw and manifest.json")
    args = p.parse_args()
    data_dir = os.path.join(HERE, "data")
    raw_dir = os.path.join(data_dir, "raw")
    os.makedirs(raw_dir, exist_ok=True)
    manifest_path = os.path.join(HERE, "manifest.json")

    if args.skip_download:
        entries = json.load(open(manifest_path))
        included = [e for e in entries if e["included"]]
    else:
        api = HfApi()
        entries = list_collections(api)
        included = select(entries)
        json.dump(entries, open(manifest_path, "w"), indent=1)
        for i, e in enumerate(included):
            print(f"[{i + 1}/{len(included)}] download {e['id']} ({len(e['transcripts'])} files)", flush=True)
            download(e, raw_dir)

    rng = np.random.RandomState(args.seed)
    build_log = {"seed": args.seed, "test_rule": "per study: min(100, floor(0.1 * rows_kept)), row-level",
                 "markers": "letter responses keep [HUMAN_RESPONSE]X[/HUMAN_RESPONSE]", "studies": {}}
    totals = Counter()
    with open(os.path.join(data_dir, "train.jsonl"), "w") as ftr, open(os.path.join(data_dir, "test.jsonl"), "w") as fte:
        for e in sorted(included, key=lambda e: e["id"]):
            rows, log = load_study(e, raw_dir)
            n_test = min(100, math.floor(0.1 * len(rows)))
            perm = rng.permutation(len(rows))
            test_idx = set(perm[:n_test].tolist())
            for i, r in enumerate(rows):
                (fte if i in test_idx else ftr).write(json.dumps(r) + "\n")
            log["n_test"], log["n_train"] = n_test, len(rows) - n_test
            build_log["studies"][r["study"] if rows else e["id"].split("/")[1]] = log
            for k in ("rows_raw", "rows_kept", "choices", "stripped", "n_test", "n_train", "stray_markers"):
                totals[k] += log[k]
            totals["experiments_kept"] += sum(1 for x in log["experiments"].values() if x.get("rows_kept", 0) > 0)
            totals["studies_kept"] += int(len(rows) > 0)
            print(f"{e['id'].split('/')[1]:40s} rows {log['rows_kept']:6d}/{log['rows_raw']:6d} choices {log['choices']:9d} "
                  f"test {n_test:3d}", flush=True)
    build_log["totals"] = dict(totals)
    json.dump(build_log, open(os.path.join(data_dir, "build_log.json"), "w"), indent=1)
    print("\nincluded datasets", len(included), "| totals", dict(totals))


if __name__ == "__main__":
    main()
