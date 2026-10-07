# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/levering_2019_revisiting``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp0), with the {dims} slot kept.
INSTRUCTIONS = (
    "You will learn to classify geometric shapes into two categories, Alpha and "
    "Beta. Each shape has three features: {dims}, each taking value 1 or 2. On each "
    "trial, a shape appears and you decide which category it belongs to: press A for "
    "Alpha or B for Beta. After each answer you are told whether you were correct. "
    "You train over 25 blocks, each covering all six training shapes once.")

SINGLE_INTRO = (
    "The training phase is over and the test begins. You see each of the eight "
    "possible shapes (the six trained shapes plus two new ones). For each shape, "
    "first classify it: press A for Alpha or B for Beta. Then rate how typical "
    "that shape is of its category on a scale from 1 (not typical) to 9 (highly "
    "typical), typing one of 1, 2, 3, 4, 5, 6, 7, 8, or 9. No feedback is given.")

PAIRED_INTRO = (
    "Finally you see pairs of shapes. For each pair, decide which shape is more "
    "typical of its category: press A to pick the first shape or B to pick the "
    "second.")

# All 8 binary-feature shapes (f1, f2, f3) with values in {1, 2}.
SHAPES = [(1, 1, 1), (1, 1, 2), (1, 2, 1), (1, 2, 2),
          (2, 1, 1), (2, 1, 2), (2, 2, 1), (2, 2, 2)]

# Medin & Schwanenflugel (1981, Exp. 4) category structures, recovered from the
# data (the two extremes (1,1,1) and (2,2,2) are always the untrained items).
# LS: Alpha = sums to 4 (112, 121, 211); Beta = sums to 5 (122, 212, 221).
LS_ALPHA = {(1, 1, 2), (1, 2, 1), (2, 1, 1)}
LS_BETA = {(1, 2, 2), (2, 1, 2), (2, 2, 1)}
# NLS (XOR-like): the two corners swapped.
NLS_ALPHA = {(1, 1, 2), (1, 2, 2), (2, 1, 1)}
NLS_BETA = {(1, 2, 1), (2, 1, 2), (2, 2, 1)}
UNTRAINED = {(1, 1, 1), (2, 2, 2)}

_DIM_NAMES = ["Shape", "Color", "Size"]

_COLUMNS = [
    "participant_id", "group", "condition", "phase", "response_type", "trial",
    "block", "response", "response_label", "correct", "stimulus", "exemplar_id",
    "feature1", "feature2", "feature3", "correct_category", "trained",
    "stimulus1", "exemplar1_id", "exemplar1_feature1", "exemplar1_feature2",
    "exemplar1_feature3", "stimulus2", "exemplar2_id", "exemplar2_feature1",
    "exemplar2_feature2", "exemplar2_feature3", "response_exemplar", "cbal_a",
    "cbal_b", "cbal_c", "cbal_d", "dim_a", "dim_b", "dim_c"]


def _stimulus(shape):
    return f"x-{shape[0]}{shape[1]}{shape[2]}.jpg"


def _random_agent(prompt, choice_options):
    return str(np.random.choice(choice_options))


class CategoryLearning:
    """LS/NLS category learning with typicality tests, Experiment 1 of Levering,
    Conaway & Kurtz (2020), "Revisiting the linear separability constraint",
    Memory & Cognition, 48(3), 335-347.

    Design (Method: Stimuli and category structures / Procedure, pp. 339-340):
    three binary dimensions (Shape, Color/shading, Size). 25 training blocks, each
    presenting all six trained examples once (random order per block), with
    Alpha/Beta classification and correctness feedback. Then a test phase
    classifying the eight possible shapes (six trained + two untrained) in random
    order, each followed by a 1-9 typicality rating with no feedback, then a
    paired typicality-choice test of six randomly chosen shape pairs.

    ASSUMPTION: the paper's Method only describes the single-exemplar typicality
    rating; the paired typicality-choice test in the shipped data is not in the
    main text. Six random distinct shape pairs per participant are used to match
    the data's 16 distinct pair patterns across participants.

    ASSUMPTION: group assignment is drawn uniformly (50/50), whereas the paper
    randomly assigned 144 LS and 126 NLS participants.

    ASSUMPTION: physical counterbalancing codes (dim_a/b/c permutation, cbal_a-d)
    are not recoverable and are drawn uniformly at random; they do not appear in
    the transcript text.

    The DataFrame matches exp0.csv minus ``rt``.
    """

    def __init__(self):
        self.name = "levering_2019_revisiting_exp0"
        self.num_blocks = 25

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        part_counter = 0
        for participant in tqdm(range(num_simulations)):
            part_counter += 1
            dims = list(np.random.permutation(_DIM_NAMES))
            dim_a, dim_b, dim_c = dims[0], dims[1], dims[2]
            group = 1 if np.random.rand() < 0.5 else 2
            condition = "ls" if group == 1 else "nls"
            cbal = [int(np.random.randint(24)),
                    int(np.random.randint(2)),
                    int(np.random.randint(2)),
                    int(np.random.randint(2))]

            exemplar_of = {shape: int(eid) for shape, eid in
                           zip(SHAPES, np.random.permutation(8) + 1)}
            alpha = LS_ALPHA if group == 1 else NLS_ALPHA
            beta = LS_BETA if group == 1 else NLS_BETA

            def category_of(shape):
                if shape in alpha:
                    return "Alpha"
                if shape in beta:
                    return "Beta"
                return None

            def eid_of(shape):
                return float(exemplar_of[shape])

            def add_exemplar(shape):
                return (f"a shape with {dim_a} {shape[0]}, {dim_b} {shape[1]}, "
                        f"{dim_c} {shape[2]}")

            def common(phase, rtype, block):
                return {"participant_id": pid, "group": group,
                        "condition": condition, "phase": phase,
                        "response_type": rtype, "block": block,
                        "stimulus1": np.nan, "exemplar1_id": np.nan,
                        "exemplar1_feature1": np.nan, "exemplar1_feature2": np.nan,
                        "exemplar1_feature3": np.nan, "stimulus2": np.nan,
                        "exemplar2_id": np.nan, "exemplar2_feature1": np.nan,
                        "exemplar2_feature2": np.nan, "exemplar2_feature3": np.nan,
                        "response_exemplar": np.nan,
                        "cbal_a": cbal[0], "cbal_b": cbal[1], "cbal_c": cbal[2],
                        "cbal_d": cbal[3], "dim_a": dim_a, "dim_b": dim_b,
                        "dim_c": dim_c}

            lines = [INSTRUCTIONS.format(
                dims=f"{dim_a}, {dim_b}, and {dim_c}")]
            trial = 0
            pid = f"{group}_{part_counter:02d}"

            # ---- training: 25 blocks x 6 trained exemplars ----
            trained_shapes = [s for s in SHAPES if s not in UNTRAINED]
            for block in range(self.num_blocks):
                if max_chars is not None and len("\n".join(lines)) >= max_chars:
                    break
                order = list(trained_shapes)
                np.random.shuffle(order)
                for shape in order:
                    desc = add_exemplar(shape)
                    lines.append(
                        f"You see {desc}. You decide it belongs to [HUMAN_RESPONSE]")
                    letter = agent("\n".join(lines), choice_options=["A", "B"])
                    label = "Alpha" if letter == "A" else "Beta"
                    lines[-1] += f"{letter}[/HUMAN_RESPONSE]."
                    cat = category_of(shape)
                    correct = 1 if label == cat else 0
                    ok = "Correct." if correct else "Incorrect."
                    lines[-1] += f" {ok} The correct category was {cat}."
                    rows.append({
                        **common("training", "classification", block),
                        "trial": trial, "response": 0 if label == "Alpha" else 1,
                        "response_label": label, "correct": float(correct),
                        "stimulus": _stimulus(shape), "exemplar_id": eid_of(shape),
                        "feature1": shape[0], "feature2": shape[1],
                        "feature3": shape[2], "correct_category": cat,
                        "trained": np.nan})
                    trial += 1

            # ---- single typicality test: classify + rate each of the 8 ----
            if max_chars is None or len("\n".join(lines)) < max_chars:
                lines.append(SINGLE_INTRO)
                single_order = list(SHAPES)
                np.random.shuffle(single_order)
                for blk, shape in enumerate(single_order):
                    if max_chars is not None and len("\n".join(lines)) >= max_chars:
                        break
                    cat = category_of(shape)
                    trained = 1 if shape not in UNTRAINED else 0
                    lines.append(
                        f"You see {add_exemplar(shape)}. You decide it belongs to "
                        f"[HUMAN_RESPONSE]")
                    letter = agent("\n".join(lines), choice_options=["A", "B"])
                    label = "Alpha" if letter == "A" else "Beta"
                    lines[-1] += f"{letter}[/HUMAN_RESPONSE]."
                    rows.append({
                        **common("singletypicality", "classification", blk),
                        "trial": trial, "response": 0 if label == "Alpha" else 1,
                        "response_label": label,
                        "correct": (float(1 if label == cat else 0) if cat else np.nan),
                        "stimulus": _stimulus(shape), "exemplar_id": eid_of(shape),
                        "feature1": shape[0], "feature2": shape[1],
                        "feature3": shape[2], "correct_category": cat,
                        "trained": trained})
                    trial += 1
                    lines.append("You rate its typicality: [HUMAN_RESPONSE]")
                    rating = agent("\n".join(lines),
                                   choice_options=[str(i) for i in range(1, 10)])
                    lines[-1] += f"{rating}[/HUMAN_RESPONSE]."
                    rows.append({
                        **common("singletypicality", "typicality_rating", blk),
                        "trial": trial, "response": int(rating),
                        "response_label": np.nan, "correct": np.nan,
                        "stimulus": _stimulus(shape), "exemplar_id": eid_of(shape),
                        "feature1": shape[0], "feature2": shape[1],
                        "feature3": shape[2], "correct_category": cat,
                        "trained": trained})
                    trial += 1

            # ---- paired typicality-choice phase ----
            if max_chars is None or len("\n".join(lines)) < max_chars:
                lines.append(PAIRED_INTRO)
                for blk in range(6):
                    if max_chars is not None and len("\n".join(lines)) >= max_chars:
                        break
                    i1, i2 = np.random.choice(len(SHAPES), 2, replace=False)
                    shape1, shape2 = SHAPES[int(i1)], SHAPES[int(i2)]
                    lines.append(
                        f"You see {add_exemplar(shape1)} and {add_exemplar(shape2)}. "
                        f"You judge the more typical shape is [HUMAN_RESPONSE]")
                    letter = agent("\n".join(lines), choice_options=["A", "B"])
                    which = "first" if letter == "A" else "second"
                    lines[-1] += f"{letter}[/HUMAN_RESPONSE] (the {which})."
                    chosen = shape1 if letter == "A" else shape2
                    rows.append({
                        **common("pairedtypicality", "typicality_choice", blk),
                        "trial": trial, "response": 0 if letter == "A" else 1,
                        "response_label": np.nan, "correct": np.nan,
                        "stimulus": np.nan, "exemplar_id": np.nan,
                        "feature1": np.nan, "feature2": np.nan, "feature3": np.nan,
                        "correct_category": np.nan, "trained": np.nan,
                        "stimulus1": _stimulus(shape1),
                        "exemplar1_id": eid_of(shape1),
                        "exemplar1_feature1": shape1[0],
                        "exemplar1_feature2": shape1[1],
                        "exemplar1_feature3": shape1[2],
                        "stimulus2": _stimulus(shape2),
                        "exemplar2_id": eid_of(shape2),
                        "exemplar2_feature1": shape2[0],
                        "exemplar2_feature2": shape2[1],
                        "exemplar2_feature3": shape2[2],
                        "response_exemplar": eid_of(chosen)})
                    trial += 1

            prompts.append("\n".join(lines))
        df = pd.DataFrame(rows, columns=_COLUMNS)
        return df, prompts


def main():
    parser = argparse.ArgumentParser(
        description="Smoke-test this simulator with a uniform-random agent.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3,
                        help="number of simulated participants (default: 3)")
    parser.add_argument("--max-chars", type=int, default=None,
                        help="stop each participant at the block boundary at/past "
                             "this many chars")
    parser.add_argument("--seed", type=int, default=None,
                        help="numpy random seed, for reproducible runs")
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    task = CategoryLearning()
    df, prompts = task.simulate(_random_agent, args.num_simulations,
                                max_chars=args.max_chars)

    print(f"name: {task.name}")
    print(f"df shape: {df.shape}")
    print("dtypes:")
    print(df.dtypes.to_string())
    print("head:")
    print(df.head(8).to_string())
    print(f"prompt lengths: {[len(p) for p in prompts]}")
    for i, p in enumerate(prompts):
        first = p.splitlines()[0]
        if len(first) > 180:
            first = first[:90] + " … " + first[-90:]
        print(f"participant {i} first line: {first}")
    print("=" * 78)
    print("first prompt, head:")
    print(prompts[0][:600])
    print("...")
    print("first prompt, tail:")
    print(prompts[0][-300:])


if __name__ == "__main__":
    main()