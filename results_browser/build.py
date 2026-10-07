"""Build the static results browser: one landing page plus one page per study.

Sources (all read-only):
- results_reports/<run>.md: per-study NLL (train/test), parameters, Laplace log marginal likelihood
- psych201_agentic/results_effects/trained_<run>_temp1.json: behavioral effects of simulated participants
- psych201_agentic/experiments.json: experiments, task class, selected effects
- psych201_agentic/manifest.json: Hugging-Brain tags and notes
- psych201_agentic/hf/<study>/README.md: "## Experiment summary" of the dataset card
- psych201_agentic/hf/<study>/analysis.py: verbal effect descriptions (module docstring, "- <effect> (<exp>): ...")
- utils.load_split: held-out transcripts from the Hugging Face Hub (one example per condition)

Usage (from core-model/): python results_browser/build.py
Output: results_browser/site/ (open site/index.html in a browser; no server needed).
"""

import html
import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # core-model/
sys.path.insert(0, str(ROOT))
from utils import load_split  # noqa: E402
OUT = Path(__file__).resolve().parent / "site"
AGENTIC = ROOT / "psych201_agentic"

# (key, label, report run name, has effects, description)
MODELS = [
    ("core", "CORE", "core-phoneme-d128-L6-fgT-wd0.5-h4-lrdelta-2209", True,
     "Reference: phonemes, 6 layers, delta rule, forgetting"),
    ("core_l1", "CORE (no hierarchy)", "core-phoneme-d128-L1-fgT-wd0.5-h4-lrdelta-2209", True,
     "Ablation: 1 layer instead of 6"),
    ("core_nofg", "CORE (no forgetting)", "core-phoneme-d128-L6-fgF-wd0.5-h4-lrdelta-2209", True,
     "Ablation: forget gate removed"),
    ("core_hebb", "CORE (no prediction errors)", "core-phoneme-d128-L6-fgT-wd0.5-h4-lrhebbian-2209", True,
     "Ablation: Hebbian rule instead of delta rule"),
    ("core_bpe", "CORE (no phonemes)", "core-bpe-d128-L6-fgT-wd0.5-h4-lrdelta-2209", True,
     "Ablation: BPE tokens instead of phonemes"),
    ("transformer", "Transformer", "transformer-bpe-d128-L6-wd0.5-h4-2209", False,
     "Baseline: matched configuration (d128, 6 layers, 4 heads, BPE)"),
    ("centaur", "Centaur", "marcelbinz-Llama-3.1-Centaur-70B-adapter", False,
     "Baseline: Llama-3.1-Centaur-70B, test split only"),
]
CONDITION_KEYS = ["condition", "group", "age_group", "version"]  # meta keys that define a condition
MAP_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7"]  # dataviz categorical, validated
MAP_COLORS_DARK = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300", "#9085e9"]

# Model equations (LaTeX, one per line), shown on the landing page; None = no equations (Centaur).
# CORE: paper/main.tex Eqs. 1-4 plus embedding, residual stream and read-out (text of the Results and Methods). Transformer: fla TransformerConfig defaults (pre-norm, RoPE, SwiGLU, final RMSNorm).
CORE_EQS = [
    r"\mathbf{x}_t = \mathrm{Embedding}(s_t)",
    r"\mathbf{H}_t = \mathbf{H}_{t-1}\,\mathrm{diag}(\boldsymbol{\alpha}_t) + \mathrm{diag}(\boldsymbol{\beta}_t)\,\mathbf{v}_t\,\mathbf{k}_t^{\top}",
    r"\boldsymbol{\alpha}_t = \sigma(\mathbf{W}^{\alpha}\mathbf{x}_t)",
    r"\mathbf{k}_t = \phi(\mathbf{W}^{k}\mathbf{x}_t)",
    r"\mathbf{y}_t = \mathbf{H}_t\,\mathbf{q}_t",
    r"\mathbf{q}_t = \phi(\mathbf{W}^{q}\mathbf{x}_t)",
    r"\mathbf{v}_t = \mathbf{x}_t - \mathbf{H}_{t-1}\,\mathrm{diag}(\boldsymbol{\alpha}_t)\,\mathbf{k}_t",
    r"\boldsymbol{\beta}_t = \sigma(\mathbf{W}^{\beta}\mathbf{x}_t)",
    r"\mathbf{x}_t^{(\ell+1)} = \mathbf{x}_t^{(\ell)} + \mathbf{y}_t^{(\ell)}",
    r"p(r_{t+1}) = \mathrm{softmax}\bigl(\mathbf{W}^{p}\mathbf{x}_t^{(L+1)}\bigr)",
]
ABLATION_NOTE = "Everything else as in CORE."
MODEL_EQS = {
    "core": (CORE_EQS, ""),
    "core_l1": ([r"L = 1"], ABLATION_NOTE),
    "core_nofg": ([r"\mathbf{H}_t = \mathbf{H}_{t-1} + \mathrm{diag}(\boldsymbol{\beta}_t)\,\mathbf{v}_t\,\mathbf{k}_t^{\top}",
                   r"\mathbf{v}_t = \mathbf{x}_t - \mathbf{H}_{t-1}\mathbf{k}_t"], ABLATION_NOTE),
    "core_hebb": ([r"\mathbf{v}_t = \mathbf{x}_t"], ABLATION_NOTE),
    "core_bpe": ([r"s_t \in \text{BPE tokens}"], ABLATION_NOTE),
    "transformer": ([
        r"\mathbf{x}_t^{(1)} = \mathrm{Embedding}(s_t)",
        r"\mathbf{q}_t = \mathbf{R}_t\,\mathbf{W}^{q}\,\mathrm{RMSNorm}(\mathbf{x}_t^{(\ell)})",
        r"\mathbf{k}_t = \mathbf{R}_t\,\mathbf{W}^{k}\,\mathrm{RMSNorm}(\mathbf{x}_t^{(\ell)})",
        r"\mathbf{v}_t = \mathbf{W}^{v}\,\mathrm{RMSNorm}(\mathbf{x}_t^{(\ell)})",
        r"\mathbf{y}_t = \sum_{i \le t} \mathrm{softmax}_i\!\left(\frac{\mathbf{q}_t^{\top}\mathbf{k}_i}{\sqrt{d_h}}\right)\mathbf{v}_i",
        r"\mathbf{h}_t^{(\ell)} = \mathbf{x}_t^{(\ell)} + \mathbf{W}^{o}\,\mathbf{y}_t",
        r"\mathbf{x}_t^{(\ell+1)} = \mathbf{h}_t^{(\ell)} + \mathrm{MLP}\bigl(\mathrm{RMSNorm}(\mathbf{h}_t^{(\ell)})\bigr)",
        r"\mathrm{MLP}(\mathbf{z}) = \mathbf{W}^{\mathrm{down}}\bigl(\mathrm{SiLU}(\mathbf{W}^{\mathrm{gate}}\mathbf{z}) \odot \mathbf{W}^{\mathrm{up}}\mathbf{z}\bigr)",
        r"p(r_{t+1}) = \mathrm{softmax}\bigl(\mathbf{W}^{p}\,\mathrm{RMSNorm}(\mathbf{x}_t^{(L+1)})\bigr)",
    ], ""),
    "centaur": (None, ""),
}


def parse_report(path):
    text = path.read_text()
    params = re.search(r"parameters: ([\d,]+) total", text)
    lml = re.search(r"log marginal likelihood[^:]*: (-?[\d.]+)", text)
    section = text.split("## NLL", 1)[1].split("\n## ", 1)[0]
    lines = [l for l in section.splitlines() if l.startswith("|")]
    header = [c.strip() for c in lines[0].strip("|").split("|")]
    rows = {}
    for line in lines[2:]:
        cells = [c.strip().strip("*") for c in line.strip("|").split("|")]
        rows[cells[0]] = {h: float(c) for h, c in zip(header[1:], cells[1:])}
    return {
        "params": int(params.group(1).replace(",", "")) if params else None,
        "lml": float(lml.group(1)) if lml else None,
        "rows": rows,
    }


def load_transcripts():
    """First row per (experiment, condition), in file order: test split; train split for experiments without test rows.
    Also returns data set totals over both splits (one row = one session)."""
    examples = defaultdict(dict)  # experiment -> condition label -> row
    n_sessions, n_test_sessions, n_choices = 0, 0, 0
    for split in ("test", "train"):
        in_test = set(examples)
        for row in load_split(split):
            n_sessions += 1
            n_test_sessions += split == "test"
            n_choices += row["n_choices"]
            if row["experiment"] in in_test:
                continue
            meta = json.loads(row["meta"])
            parts = [f"{k}={meta[k]}" for k in CONDITION_KEYS if k in meta]
            label = ", ".join(parts) if parts else "all participants"
            examples[row["experiment"]].setdefault(label, {
                "participant": row["participant"], "n_choices": row["n_choices"],
                "text": row["text"], "split": split,
            })
    totals = {"sessions": n_sessions, "test_sessions": n_test_sessions, "choices": n_choices}
    return examples, totals


def fmt(x, digits=4):
    if x is None:
        return "–"
    if isinstance(x, float) and x != x:
        return "–"
    if isinstance(x, (int, float)):
        return f"{x:,.{digits}f}" if isinstance(x, float) else f"{x:,}"
    return html.escape(str(x))


def fmt_effect(x):
    if isinstance(x, (int, float)):
        return "–" if x != x else f"{x:+.3f}"
    if x is None:
        return "–"
    s = str(x)
    try:  # dict-like strings, e.g. "{'healthy': 0.03, ...}"
        d = json.loads(s.replace("'", '"'))
        return ", ".join(f"{html.escape(k)}: {v:+.3f}" for k, v in d.items())
    except (ValueError, AttributeError, TypeError):
        return html.escape(s)


def highlight(text):
    escaped = html.escape(text)
    return re.sub(r"\[HUMAN_RESPONSE\](.*?)\[/HUMAN_RESPONSE\]", r'<mark title="human response">\1</mark>', escaped)


def display_order(reports):
    """CORE models by -log marginal likelihood (best first), then the baselines in their MODELS order."""
    core_models = sorted((m for m in MODELS if m[0].startswith("core")), key=lambda m: -reports[m[0]]["lml"])
    return core_models + [m for m in MODELS if not m[0].startswith("core")]


def experiment_summary(study):
    """Text of the "## Experiment summary" section of the dataset card, or "" if absent."""
    path = AGENTIC / "hf" / study / "README.md"
    if not path.exists():
        return ""
    m = re.search(r"^## Experiment summary\n(.*?)(?=^## |\Z)", path.read_text(), re.M | re.S)
    return m.group(1).strip() if m else ""


def effect_descriptions(study):
    """{effect name: description} from the "- <effect> (<exp>): <text>" bullets of the analysis.py docstring."""
    src = (AGENTIC / "hf" / study / "analysis.py").read_text()
    doc = re.search(r'"""(.*?)"""', src, re.S)
    out = {}
    for m in re.finditer(r"^- `?(\w+)`?\s*(?:\([^)]*\))?\s*:\s*(.*?)(?=^- |^\s*$|\Z)", doc.group(1) if doc else "", re.M | re.S):
        out[m.group(1)] = " ".join(m.group(2).split())
    return out


def page(title, body, depth, head=""):
    prefix = "../" * depth
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{prefix}style.css">{head}
</head><body>
<main>{body}</main>
<footer><div class="wrap">Built from <code>results_reports/</code> and <code>psych201_agentic/results_effects/</code> (runs 2209) by <code>results_browser/build.py</code>.</div></footer>
<script src="{prefix}app.js"></script>
</body></html>
"""


def tag_chips(tags, link=True):
    out = []
    for t in tags:
        kind, _, val = t.partition(":")
        if kind == "paradigm":
            out.append(f'<span class="chip paradigm">{html.escape(val)}</span>')
        elif not val:
            out.append(f'<span class="chip minor">{html.escape(t)}</span>')
    return " ".join(out)


def tiles(items):
    """items: (label, value, sub) triples -> a row of stat tiles."""
    out = "".join(f'<div class="tile"><div class="tile-label">{label}</div><div class="tile-value">{value}</div>'
                  f'<div class="tile-sub">{sub}</div></div>' for label, value, sub in items)
    return f'<div class="tiles">{out}</div>'


def nll_table(study, reports, models):
    means = {k: reports[k]["rows"][study]["mean (test)"] for k, *_ in MODELS if study in reports[k]["rows"]}
    best = min(means, key=means.get)
    worst = max(reports[k]["rows"][study]["nll (test)"] for k in means)
    rows = []
    for key, label, *_ in models:
        r = reports[key]["rows"].get(study)
        if r is None:
            continue
        m = r["mean (test)"]
        width = 100 * r["nll (test)"] / worst
        cls = ' class="best"' if key == best else ""
        family = "core" if key.startswith("core") else "base"
        badge = ' <span class="pill best-pill">best</span>' if key == best else ""
        rows.append(
            f"<tr{cls}><td>{label}{badge}</td>"
            f'<td class="barcell" data-v="{r["nll (test)"]}" title="{label}: {fmt(r["nll (test)"], 1)} nats">'
            f'<span class="track"><span class="bar {family}" style="width:{width:.1f}%"></span></span>'
            f'<span class="num">{fmt(r["nll (test)"], 1)}</span></td>'
            f'<td class="num" data-v="{m}">{m:.4f}</td>'
            f'<td class="num" data-v="{r["n (test)"]:.0f}">{int(r["n (test)"]):,}</td>'
            f'<td class="num" data-v="{r.get("mean (train)", "")}">{fmt(r.get("mean (train)"))}</td>'
            f'<td class="num" data-v="{r.get("n (train)", "")}">{fmt(int(r["n (train)"])) if "n (train)" in r else "–"}</td></tr>'
        )
    return f"""<div class="scroll"><table class="sortable">
<thead><tr><th>model</th><th>PNLL</th><th class="num">test NLL (avg)</th><th class="num">test responses</th>
<th class="num">train NLL (avg)</th><th class="num">train responses</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>"""


def effects_table(study, effects, models):
    eff_models = [(k, label) for k, label, _, has, _ in models if has]
    by_effect = {}  # (effect, experiment) -> {model: row}
    for key, _ in eff_models:
        for row in effects[key]:
            if row["study"] == study:
                by_effect.setdefault((row["effect_name"], row["experiment"]), {})[key] = row
    if not by_effect:
        return '<p class="hint">No behavioral effects were simulated for this study.</p>'
    head = "".join(f"<th>{label}</th>" for _, label in eff_models)
    descriptions = effect_descriptions(study)
    rows = []
    for i, ((name, exp), per_model) in enumerate(by_effect.items()):
        paper = next(iter(per_model.values()))["original_effect_size"]
        cells = []
        for key, _ in eff_models:
            r = per_model.get(key)
            if r is None:
                cells.append("<td>–</td>")
            elif r["status"] != "ok":
                cells.append(f'<td class="err" title="{html.escape(str(r["error"]))}">{html.escape(r["status"])}</td>')
            else:
                ok = r["reproduced"]
                pill = '<span class="pill yes">✓ yes</span>' if ok else '<span class="pill no">✗ no</span>'
                cells.append(f'<td>{pill}<div class="effect-val">{fmt_effect(r["effect_size"])}</div></td>')
        desc = descriptions.get(name) or descriptions.get(name.removesuffix(f"_{exp}"))
        toggle = (f'<button class="eq-toggle" data-target="desc-{i}" aria-expanded="false">Description</button>'
                  if desc else "")
        rows.append(f"<tr><td><code>{html.escape(name)}</code>{toggle}</td><td>{html.escape(exp)}</td>"
                    f'<td class="num">{fmt_effect(paper)}</td>{"".join(cells)}</tr>')
        if desc:
            rows.append(f'<tr class="eq-row" id="desc-{i}" hidden><td colspan="{3 + len(eff_models)}">'
                        f'<p class="effect-desc">{html.escape(desc)}</p></td></tr>')
    return f"""<div class="scroll"><table class="effects">
<thead><tr><th>effect</th><th>experiment</th><th class="num">paper</th>{head}</tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>"""


def transcript_block(study, transcripts):
    options, blocks = [], []
    i = 0
    for exp_file in sorted(e for e in transcripts if e.startswith(study + "/")):
        exp = exp_file.split("/", 1)[1].removesuffix(".csv")
        for label, ex in transcripts[exp_file].items():
            tid = f"t{i}"
            options.append(f'<option value="{tid}">{exp} · {html.escape(label)}</option>')
            hidden = "" if i == 0 else " hidden"
            blocks.append(
                f'<div class="transcript" id="{tid}"{hidden}>'
                f'<pre>{highlight(ex["text"])}</pre></div>')
            i += 1
    if not options:
        return '<p class="hint">No held-out transcript for this study.</p>'
    return (f'<label class="picker">Experiment and condition '
            f'<select id="transcript-select">{"".join(options)}</select></label>{"".join(blocks)}')


def study_page(study, info, exps, reports, effects, transcripts, models):
    tags = tag_chips(info["tags"]) if info else ""
    exp_rows = []
    for e in exps:
        n_cond = len(transcripts.get(f"{study}/{e['exp']}.csv", {}))
        eff = ", ".join(f"<code>{html.escape(x)}</code>" for x in e["effects"]) or "–"
        exp_rows.append(
            f"<tr><td>{e['exp']}</td><td>{html.escape(e['task_class'])}</td>"
            f'<td class="num">{e["participants"]:,}</td><td class="num">{e["choices"]:,}</td>'
            f'<td class="num">{n_cond}</td><td>{"yes" if e["selected"] else "no"}</td>'
            f"<td>{eff}</td></tr>")
    means = {k: reports[k]["rows"][study]["mean (test)"] for k, *_ in MODELS if study in reports[k]["rows"]}
    rank = sorted(means.values()).index(means["core"]) + 1
    core_eff = [r for r in effects["core"] if r["study"] == study]
    n_rep = sum(r["reproduced"] for r in core_eff if r["status"] == "ok")
    row = reports["core"]["rows"][study]
    n_choices = int(row["n (test)"] + row.get("n (train)", 0))
    summary = tiles([
        ("Responses", f"{n_choices:,}", f'{int(row["n (test)"]):,} held out'),
        ("CORE effects", f"{n_rep} / {len(core_eff)}" if core_eff else "–", "" if core_eff else "no effects simulated"),
        ("CORE test NLL (avg)", f'{means["core"]:.3f}', f"rank {rank} of {len(means)} models"),
        ("Best model", next(label for k, label, *_ in MODELS if k == min(means, key=means.get)), f'test NLL (avg) {min(means.values()):.3f}'),
    ])
    body = f"""
<nav class="crumbs"><a href="../index.html">All studies</a> / {html.escape(study)}</nav>
<h1>{html.escape(study)}</h1>
<p class="tags">{tags}</p>
<p>{html.escape(experiment_summary(study))}</p>
{summary}
<section class="card" id="likelihood"><h2>Likelihood of human responses</h2>{nll_table(study, reports, models)}</section>
<section class="card" id="experiments"><h2>Experiments</h2><div class="scroll"><table>
<thead><tr><th>exp</th><th>task class</th><th class="num">participants</th><th class="num">responses</th><th class="num">conditions</th><th>simulated</th><th>effects</th></tr></thead>
<tbody>{''.join(exp_rows)}</tbody></table></div></section>
<section class="card" id="effects"><h2>Behavioral effects</h2>{effects_table(study, effects, models)}</section>
<section class="card" id="transcript"><h2>Transcript</h2>{transcript_block(study, transcripts)}</section>
"""
    return page(study, body, depth=1)


def map_points(embedding, manifest, exps_by_study, reports):
    """Points of the experiment map: top-7 paradigms (by experiment count) get a color, the rest are 'other'."""
    paradigm = {s: next((t.split(":", 1)[1] for t in m["tags"] if t.startswith("paradigm:")), "unknown") for s, m in manifest.items()}
    task_class = {f'{e["study"]}/{e["exp"]}.csv': e["task_class"] for es in exps_by_study.values() for e in es}
    participants = {f'{e["study"]}/{e["exp"]}.csv': e["participants"] for es in exps_by_study.values() for e in es}
    counts = defaultdict(int)
    for p in embedding["points"]:
        counts[paradigm.get(p["experiment"].split("/")[0], "unknown")] += 1
    top = sorted(counts, key=lambda k: (-counts[k], k))[:len(MAP_COLORS)]
    points = []
    for p in embedding["points"]:
        study, exp = p["experiment"].split("/")
        par = paradigm.get(study, "unknown")
        points.append({"x": p["x"], "y": p["y"], "study": study, "exp": exp.removesuffix(".csv"), "paradigm": par,
                       "group": top.index(par) if par in top else -1, "task": task_class.get(p["experiment"], "–"),
                       "participants": participants.get(p["experiment"]),
                       "core": reports["core"]["rows"].get(study, {}).get("mean (test)"),
                       "transformer": reports["transformer"]["rows"].get(study, {}).get("mean (test)")})
    groups = [{"name": t, "n": counts[t], "light": MAP_COLORS[i], "dark": MAP_COLORS_DARK[i]} for i, t in enumerate(top)]
    groups.append({"name": "other", "n": sum(counts[t] for t in counts if t not in top), "light": "#898781", "dark": "#898781"})
    return {"points": points, "groups": groups}


def index_page(studies, manifest, exps_by_study, reports, effects, n_experiments, totals, embedding):
    # Model summary
    mrows = []
    for key, label, run, has, _ in display_order(reports):
        rep = reports[key]
        total = rep["rows"]["TOTAL"]
        if has:
            ok = [r for r in effects[key] if r["status"] == "ok"]
            eff = f'{sum(r["reproduced"] for r in ok)} / {len(effects[key])}'
        else:
            eff = "–"
        nlml = -rep["lml"] if rep["lml"] is not None else None
        eqs, note = MODEL_EQS[key]
        mrows.append(
            f"<tr><td><b>{label}</b>"
            + (f'<button class="eq-toggle" data-target="eq-{key}" aria-expanded="false">Equations</button>' if eqs else "")
            + "</td>"
            f'<td class="num" data-v="{rep["params"] or ""}">{fmt(rep["params"])}</td>'
            f'<td class="num" data-v="{nlml or ""}">{fmt(nlml, 1)}</td>'
            f'<td class="num" data-v="{total["nll (test)"]}">{fmt(total["nll (test)"], 1)}</td>'
            f'<td class="num" data-v="{total["mean (test)"]}">{total["mean (test)"]:.4f}</td>'
            f"<td class='num'>{eff}</td></tr>")
        if eqs:
            items = "".join(f'<li><div class="tex">{html.escape(tex)}</div></li>' for tex in eqs)
            note_html = f'<p class="hint">{html.escape(note)}</p>' if note else ""
            mrows.append(f'<tr class="eq-row" id="eq-{key}" hidden><td colspan="6"><ol class="eqs">{items}</ol>{note_html}</td></tr>')

    # Study rows
    srows = []
    for s in studies:
        info = manifest.get(s, {})
        paradigms = [t.split(":", 1)[1] for t in info.get("tags", []) if t.startswith("paradigm:")]
        means = {k: reports[k]["rows"][s]["mean (test)"] for k, *_ in MODELS if s in reports[k]["rows"]}
        best = min(means, key=means.get)
        best_label = next(label for k, label, *_ in MODELS if k == best)
        core_eff = [r for r in effects["core"] if r["study"] == s]
        n_rep = sum(r["reproduced"] for r in core_eff if r["status"] == "ok")
        eff_cell = f"{n_rep} / {len(core_eff)}" if core_eff else "–"
        eff_v = n_rep / len(core_eff) if core_eff else -1
        n_test = int(reports["core"]["rows"][s]["n (test)"])
        cells = "".join(f'<td class="num" data-v="{means.get(k, "")}">{fmt(means.get(k))}</td>'
                        for k in ("core", "transformer", "centaur"))
        srows.append(
            f"<tr>"
            f'<td><a href="studies/{s}.html">{html.escape(s)}</a></td>'
            f"<td>{tag_chips(['paradigm:' + p for p in paradigms])}</td>"
            f'<td class="num">{len(exps_by_study.get(s, []))}</td>'
            f'<td class="num" data-v="{n_test}">{n_test:,}</td>'
            f'<td class="num" data-v="{eff_v}">{eff_cell}</td>{cells}'
            f'<td class="nowrap"><span class="pill {"core" if best.startswith("core") else "base"}">{best_label}</span></td></tr>')
    summary = tiles([
        ("Experiments", f"{n_experiments}", ""),
        ("Studies", f"{len(studies)}", ""),
        ("Sessions", f'{totals["sessions"]:,}', f'{totals["test_sessions"]:,} held out'),
        ("Responses", f'{totals["choices"]:,}', f'{int(reports["core"]["rows"]["TOTAL"]["n (test)"]):,} held out'),
    ])
    map_json = json.dumps(map_points(embedding, manifest, exps_by_study, reports)).replace("</", "<\\/")
    body = f"""
<div class="hero"><h1><span class="accent">CORE</span> results</h1></div>
{summary}
<section class="card"><h2>Models</h2><div class="scroll"><table class="models">
<thead><tr><th>model</th><th class="num">parameters</th><th class="num">NLML</th>
<th class="num">PNLL</th><th class="num">test NLL (avg)</th><th class="num">effects reproduced</th></tr></thead>
<tbody>{''.join(mrows)}</tbody></table></div></section>
<section class="card" id="map-section"><h2>Experiment map</h2>
<div id="map-legend" class="legend"></div>
<div id="map" class="map"></div>
<div id="map-tip" class="tip" hidden></div>
<script id="map-data" type="application/json">{map_json}</script>
</section>
<section class="card" id="studies-section"><h2>Studies</h2>
<div class="scroll"><table class="sortable" id="studies">
<thead><tr><th>study</th><th>paradigm</th><th class="num">exps</th><th class="num">responses</th>
<th class="num">CORE effects</th><th class="num">CORE</th><th class="num">Transf.</th><th class="num">Centaur</th><th>best</th></tr></thead>
<tbody>{''.join(srows)}</tbody></table></div></section>
"""
    katex = ('\n<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">'
             '\n<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>')
    return page("CORE results", body, depth=0, head=katex)


def main():
    reports = {key: parse_report(ROOT / "results_reports" / f"{run}.md") for key, _, run, *_ in MODELS}
    effects = {key: json.load(open(AGENTIC / "results_effects" / f"trained_{run}_temp1.json"))["rows"]
               for key, _, run, has, _ in MODELS if has}
    manifest = {m["id"].split("/", 1)[1]: m for m in json.load(open(AGENTIC / "manifest.json")) if m["included"]}
    exps_by_study = defaultdict(list)
    for e in json.load(open(AGENTIC / "experiments.json")):
        exps_by_study[e["study"]].append(e)
    transcripts, totals = load_transcripts()
    studies = sorted(s for s in reports["core"]["rows"] if s != "TOTAL")

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "studies").mkdir(parents=True)
    here = Path(__file__).resolve().parent
    shutil.copy(here / "style.css", OUT / "style.css")
    shutil.copy(here / "app.js", OUT / "app.js")
    embedding = json.load(open(Path(__file__).resolve().parent / "embedding.json"))
    (OUT / "index.html").write_text(index_page(studies, manifest, exps_by_study, reports, effects, len(transcripts), totals, embedding))
    for s in studies:
        (OUT / "studies" / f"{s}.html").write_text(
            study_page(s, manifest.get(s), exps_by_study.get(s, []), reports, effects, transcripts, display_order(reports)))
    print(f"wrote {len(studies)} study pages to {OUT}")


if __name__ == "__main__":
    main()
