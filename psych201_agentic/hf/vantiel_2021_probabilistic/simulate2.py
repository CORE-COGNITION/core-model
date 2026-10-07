# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp2 (Experiment 2a: monotonicity pretest) of
``Hugging-Brain/vantiel_2021_probabilistic``, format-identical to the repo's
``transcripts2.jsonl``.

``uv run simulate2.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp2).
INSTRUCTIONS = (
    "You will judge whether logical arguments are valid. An argument is valid "
    "when the conclusion is necessarily true if the premise is true. For each "
    "argument, press A if it is valid or B if it is invalid. Example: 'Angela "
    "owns a dog. Therefore, Angela owns a pet.' is valid; 'Angela owns a pet. "
    "Therefore, Angela owns a dog.' is invalid.\n"
)

# Weak predicate (stored in the data) -> its entailed strong counterpart.
# Source: supplement Table 2, "Weak" / "Strong" columns (as in build_jsonl.py).
STRONG = {
    "saw a tree": "saw an oak",
    "is from Texas": "is from Houston",
    "is from Illinois": "is from Chicago",
    "travelled to France": "travelled to Paris",
    "used a herb": "used rosemary",
    "bought a flower": "bought a rose",
    "ate vegetables": "ate carrots",
    "owns a pet": "owns a dog",
    "was drinking a soda": "was drinking a Pepsi",
    "bought a gemstone": "bought a diamond",
    "drank alcohol": "drank wine",
    "ordered meat": "ordered steak",
    "owns a vehicle": "owns a truck",
    "owns a weapon": "owns a sword",
    "ordered fish": "ordered salmon",
    "read a novel": "read 'Moby Dick'",
    "played a card game": "played poker",
    "watched a movie": "watched 'Pulp Fiction'",
    "saw a bird": "saw an eagle",
    "ate a fruit": "ate an apple",
    "saw an animal": "saw a lion",
    "saw an insect": "saw a cockroach",
    "travelled to Russia": "travelled to Moscow",
    "travelled to Japan": "travelled to Tokyo",
    "is from California": "is from San Francisco",
}

VALID_TOKEN = {"1": "A", "0": "B"}  # A = valid, B = invalid (pinned in instructions)


class MonotonicityPretest:
    """Monotonicity pretest, Experiment 2a of van Tiel, Franke & Sauerland
    (2021), PNAS 118(9) e2005453118.

    Design (Materials and Methods, Exp 2; build_jsonl transcribe_exp2): each
    participant judges the validity of 50 individual (non-quantified)
    entailment arguments — the 25 weak/strong predicate pairs, each shown in
    both directions (strong-to-weak and weak-to-strong), in a randomized order
    per participant. A ``strong_to_weak`` argument ('premise strong, therefore
    weak') is valid; the reverse direction is invalid.

    The token mapping is fixed: A = valid (response 1), B = invalid (response
    0), pinned in the instructions, so no per-participant randomization.

    The DataFrame matches exp2.csv minus the ``rt`` reaction-time column and
    the post-hoc ``error`` column.
    """

    def __init__(self):
        self.name = "vantiel_2021_probabilistic_exp2"
        self.strong = dict(STRONG)
        self.valid_token = VALID_TOKEN

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
# 25 predicates x 2 directions = 50 trials, per participant; each
        # predicate appears once in each direction.
        slots = [(weak, d) for weak in self.strong
                 for d in ("strong_to_weak", "weak_to_strong")]
        for participant in tqdm(range(num_simulations)):
            prompt = INSTRUCTIONS
            order = np.random.permutation(len(slots)).tolist()
            for trial, idx in enumerate(order):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                weak, direction = slots[idx]
                strong = self.strong[weak]
                if direction == "strong_to_weak":
                    premise, conclusion = strong, weak
                else:
                    premise, conclusion = weak, strong
                prompt += (f"Argument: '{premise}. Therefore, {conclusion}.' "
                            f"You judge it [HUMAN_RESPONSE]")
                letter = agent(prompt, choice_options=["A", "B"])
                response = 1 if letter == "A" else 0
                prompt += f"{letter}[/HUMAN_RESPONSE] (A = valid, B = invalid).\n"
                rows.append({"participant_id": participant, "trial": trial,
                             "response": response, "condition": direction,
                             "predicate": weak})
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "condition", "predicate",
        ])
        return df, prompts


def _random_agent(prompt, choice_options):
    return str(np.random.choice(choice_options))


def main():
    parser = argparse.ArgumentParser(
        description="Smoke-test this simulator with a uniform-random agent.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3,
                        help="number of simulated participants (default: 3)")
    parser.add_argument("--max-chars", type=int, default=None,
                        help="stop each participant at the block boundary at/past this many chars")
    parser.add_argument("--seed", type=int, default=None,
                        help="numpy random seed, for reproducible runs")
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    task = MonotonicityPretest()
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