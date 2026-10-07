#!/usr/bin/env python
"""Fig. 2 of the paper: model comparison (the numbers of Table S1, as a figure).

  A  negative log marginal likelihood (NLML) of CORE, its ablations and the baselines (x does not start at 0)
  B  predictive negative log-likelihood on held-out sessions (PNLL), same models
  C  per-study PNLL per choice (mean test NLL), CORE vs. the Transformer
  D  per-study PNLL per choice (mean test NLL), CORE vs. Centaur

Inputs: results_reports/<run>.md of the 2209 runs and of Centaur (header line "log marginal likelihood", NLL table
with a TOTAL row). NLML = -log marginal likelihood; PNLL = TOTAL nll (test), 597,873 held-out choices.
Run from core-model/ with env_full:  python plotting/fig2_comparison.py   -> paper/figures/fig2_comparison.{pdf,png}; numbers printed.
"""
import os
import re

import matplotlib.pyplot as plt
import numpy as np

from fig3_latents import INK, INK2, MUTED, GRID, apply_style

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
REPORTS = os.path.join(REPO, "results_reports")
OUT = os.path.join(REPO, "paper", "figures", "fig2_comparison")

CORE = "core-phoneme-d128-L6-fgT-wd0.5-h4-lrdelta-2209"
# (label, report, group); groups and rows from top to bottom
MODELS = [
    ("CORE", CORE, "core"),
    ("$-$ hierarchy", "core-phoneme-d128-L1-fgT-wd0.5-h4-lrdelta-2209", "ablation"),
    ("$-$ forgetting", "core-phoneme-d128-L6-fgF-wd0.5-h4-lrdelta-2209", "ablation"),
    ("$-$ phonemes", "core-bpe-d128-L6-fgT-wd0.5-h4-lrdelta-2209", "ablation"),
    ("$-$ prediction errors", "core-phoneme-d128-L6-fgT-wd0.5-h4-lrhebbian-2209", "ablation"),
    ("Transformer", "transformer-bpe-d128-L6-wd0.5-h4-2209", "baseline"),
    ("Centaur", "marcelbinz-Llama-3.1-Centaur-70B-adapter", "baseline"),
]
GROUP_TITLE = {"ablation": "Ablations", "baseline": "Baselines"}  # CORE is its own group, without a heading
# dataviz reference palette: CORE blue (slot 1), its ablations a lighter step of the same ramp, baselines orange (slot 2)
COLOR = {"core": "#2a78d6", "ablation": "#86b6ef", "baseline": "#eb6834"}


def read_report(run):
    """NLML (None if the report has none), PNLL, and per-study mean test NLL per choice."""
    text = open(os.path.join(REPORTS, f"{run}.md")).read()
    m = re.search(r"log marginal likelihood[^:]*: (-?[\d.]+)", text)
    nlml = -float(m.group(1)) if m else None
    header, per_study, pnll = None, {}, None
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("| study |"):
            header = cells
            continue
        if header is None or not line.startswith("|") or line.startswith("|---"):
            continue
        row = dict(zip(header, cells))
        if row["study"] == "**TOTAL**":
            pnll = float(row["nll (test)"])
            header = None
        else:
            per_study[row["study"]] = float(row["mean (test)"])
    return nlml, pnll, per_study


def row_layout():
    """y of every model row and of every group heading (top to bottom, a gap between groups)."""
    y, rows, heads, prev = 0.0, [], [], None
    for _, _, group in MODELS:
        if group != prev:
            if prev is not None:
                y -= 0.5
            if group in GROUP_TITLE:
                heads.append((y, GROUP_TITLE[group]))
                y -= 1
            prev = group
        rows.append(y)
        y -= 1
    return rows, heads


def bars(ax, values, title, left):
    rows, heads = row_layout()
    xmax = max(v for v in values if v is not None)
    for yi, (label, _, group), v in zip(rows, MODELS, values):
        bold = "bold" if group == "core" else "normal"
        if v is None:
            ax.text(left + (xmax - left) * 0.01, yi, "N/A", va="center", ha="left", fontsize=7, color=MUTED, style="italic")
            continue
        ax.barh(yi, v, height=0.7, color=COLOR[group], linewidth=0)
        # round .5 up, as in the text (Python's round-half-to-even would print 4,592,030.5 as 4,592,030)
        ax.text(v + (xmax - left) * 0.02, yi, f"{int(v + 0.5):,}", va="center", ha="left", fontsize=7, color=INK if bold == "bold" else INK2,
                fontweight=bold)
    ax.set_axisbelow(True)
    ticks = rows + [h[0] for h in heads]
    labels = [m[0] for m in MODELS] + [h[1] for h in heads]
    ax.set_yticks(ticks)
    ax.set_yticklabels(labels, fontsize=8)
    for tick, (label, _, group) in zip(ax.get_yticklabels()[:len(MODELS)], MODELS):
        tick.set_color(INK if group == "core" else INK2)
        tick.set_fontweight("bold" if group == "core" else "normal")
    for tick in ax.get_yticklabels()[len(MODELS):]:
        tick.set_color(MUTED)
        tick.set_fontstyle("italic")
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.grid(axis="y", visible=False)
    ax.set_ylim(rows[-1] - 0.6, 0.6)
    ax.set_xlim(left, xmax + (xmax - left) * 0.3)  # bars are clipped at the left edge (x does not start at 0)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v / 1e6:g}M" if v >= 1e6 else f"{v / 1e3:,.0f}k"))
    for tick in ax.get_yticklabels():
        tick.set_horizontalalignment("left")
    ax.set_title(title, loc="left")

def scatter(ax, core, base, name):
    studies = sorted(core)
    x = np.array([core[s] for s in studies])
    yv = np.array([base[s] for s in studies])
    lo, hi = 0.18, 3.0
    ax.plot([lo, hi], [lo, hi], color=MUTED, linewidth=0.8, linestyle="--", zorder=1)
    ax.scatter(x, yv, s=16, color=COLOR["baseline"], edgecolor="white", linewidth=0.5, zorder=2)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ticks = [0.2, 0.5, 1, 2]
    for axis in (ax.xaxis, ax.yaxis):
        axis.set_major_locator(plt.FixedLocator(ticks))
        axis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}"))
        axis.set_minor_locator(plt.NullLocator())
    ax.set_aspect("equal")
    ax.set_axisbelow(True)
    ax.set_xlabel("PNLL (CORE)")
    ax.set_ylabel(f"PNLL ({name})")
    wins = int((x < yv).sum())
    ax.text(0.96, 0.06, f"CORE better in {wins} of {len(studies)} studies", transform=ax.transAxes,
            va="bottom", ha="right", fontsize=7, color=INK2, style="italic")
    ax.set_title(f"Per study against {name}", loc="left")
    return wins, len(studies)


def main():
    apply_style()
    rows = [(label, *read_report(run)) for label, run, _ in MODELS]
    nlml = [n for _, n, _, _ in rows]
    pnll = [p for _, _, p, _ in rows]

    fig = plt.figure(figsize=(7.0, 6.1))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1.25], hspace=0.45, wspace=0.75)
    ax_a, ax_b = fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])
    ax_c, ax_d = fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])
    bars(ax_a, nlml, "NLML (↓)", left=3.0e6)
    bars(ax_b, pnll, "PNLL (↓)", left=2.0e5)
    fig.canvas.draw()  # left-aligned row labels: pad = width of the longest label
    for ax in (ax_a, ax_b):
        width = max(t.get_window_extent().width for t in ax.get_yticklabels()) * 72 / fig.dpi
        ax.tick_params(axis="y", pad=width + 4)
    by = dict((label, s) for label, _, _, s in rows)
    wins_t = scatter(ax_c, by["CORE"], by["Transformer"], "Transformer")
    wins_c = scatter(ax_d, by["CORE"], by["Centaur"], "Centaur")
    # letters at the left edge of the row labels of A-B; C-D share the x of the panel above them
    from matplotlib.transforms import blended_transform_factory
    for top, bottom, (la, lb) in ((ax_a, ax_c, "AC"), (ax_b, ax_d, "BD")):
        width = max(t.get_window_extent().width for t in top.get_yticklabels()) + 4 * fig.dpi / 72
        x = (top.get_window_extent().x0 - width) / fig.bbox.width
        for ax, letter in ((top, la), (bottom, lb)):
            ax.text(x, 1.02, letter, transform=blended_transform_factory(fig.transFigure, ax.transAxes), fontsize=11,
                    fontweight="bold", color=INK, ha="left", va="bottom")

    for ext in ("pdf", "png"):
        fig.savefig(f"{OUT}.{ext}", dpi=300, bbox_inches="tight")
    for label, n, p, _ in rows:
        print(f"{label:24s} NLML {n if n is None else f'{n:,.2f}'}  PNLL {p:,.2f}")
    print(f"per study: CORE better than Transformer in {wins_t[0]}/{wins_t[1]}, than Centaur in {wins_c[0]}/{wins_c[1]}")


if __name__ == "__main__":
    main()
