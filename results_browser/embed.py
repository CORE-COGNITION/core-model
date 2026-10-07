"""2-D map of the experiments for the results browser: sentence embedding of each experiment's instructions, then UMAP.

Instructions = transcript text before the first human response, from the first row of the experiment
(test split; train split if the experiment has no test row). all-MiniLM-L6-v2 reads at most 256 word pieces.

Usage (from core-model/): python results_browser/embed.py
Output: results_browser/embedding.json (read by build.py).
"""

import json
import sys
from pathlib import Path

import umap
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent.parent  # core-model/
sys.path.insert(0, str(ROOT))
from utils import load_split  # noqa: E402
OUT = Path(__file__).resolve().parent / "embedding.json"
MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SEED = 0


def load_instructions():
    instructions = {}
    for split in ("test", "train"):
        for row in load_split(split):
            if row["experiment"] not in instructions:
                instructions[row["experiment"]] = row["text"].split("[HUMAN_RESPONSE]", 1)[0].strip()
    return instructions


def main():
    instructions = load_instructions()
    experiments = sorted(instructions)
    model = SentenceTransformer(MODEL, device="cpu")
    vectors = model.encode([instructions[e] for e in experiments], normalize_embeddings=True, show_progress_bar=False)
    xy = umap.UMAP(n_neighbors=15, min_dist=0.3, metric="cosine", random_state=SEED).fit_transform(vectors)
    points = [{"experiment": e, "x": round(float(x), 4), "y": round(float(y), 4)} for e, (x, y) in zip(experiments, xy)]
    OUT.write_text(json.dumps({"model": MODEL, "method": "UMAP (n_neighbors=15, min_dist=0.3, cosine, seed 0)",
                               "points": points}, indent=1))
    print(f"wrote {len(points)} points to {OUT}")


if __name__ == "__main__":
    main()
