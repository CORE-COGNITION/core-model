# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp3 (Experiment 2b: monotonicity) of
``Hugging-Brain/vantiel_2021_probabilistic``, format-identical to the repo's
``transcripts3.jsonl``.

``uv run simulate3.py -n 3`` smoke-tests with a uniform-random agent; or import
the module and pass ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp3).
INSTRUCTIONS = (
    "You will judge whether logical arguments are valid. An argument is valid "
    "when the conclusion is necessarily true if the premise is true. The "
    "arguments are of the form 'Q of the people P1. Therefore, Q of the people "
    "P2.', where Q is a quantity word such as 'all' or 'some'. For each "
    "argument, press A if it is valid or B if it is invalid. Example: 'All of "
    "the people ate salmon. Therefore, all of the people ate fish.' is valid; "
    "'All of the people ate fish. Therefore, all of the people ate salmon.' is "
    "invalid.\n"
)

# Weak predicate (stored in the data) -> its entailed strong counterpart.
# Source: supplement Table 1 (as in build_jsonl.py); exp3 uses the plural forms.
STRONG = {
    "are from California": "are from San Francisco",
    "are from Texas": "are from Houston",
    "ate a fruit": "ate an apple",
    "bought a flower": "bought a rose",
    "drank alcohol": "drank wine",
    "ordered fish": "ordered salmon",
    "ordered meat": "ordered steak",
    "own a pet": "own a dog",
    "own a vehicle": "own a truck",
    "own a weapon": "own a sword",
    "played a card game": "played poker",
    "read a novel": "read 'Moby Dick'",
    "saw a bird": "saw an eagle",
    "saw an animal": "saw a lion",
    "saw an insect": "saw a cockroach",
    "travelled to Japan": "travelled to Tokyo",
    "used a herb": "used rosemary",
}

QUANTIFIERS = [
    "a few", "a lot", "about half", "all", "almost all", "few", "half",
    "hardly any", "less than half", "many", "more than half", "most",
    "none", "several", "some", "the majority", "very few",
]

VALID_TOKEN = {"1": "A", "0": "B"}  # A = valid, B = invalid (pinned in instructions)


class Monotonicity:
    """Monotonicity main, Experiment 2b of van Tiel, Franke & Sauerland
    (2021), PNAS 118(9) e2005453118.

    Design (Materials and Methods, Exp 2): 17 predicate pairs were selected
    from the pretest such that P1 entails P2. For each quantity word, two
    arguments were generated: 'Q of the people P1. Therefore, Q of the people
    P2.' and its reverse. Each participant sees 34 trials: each of the 17
    predicates in both directions, and each of the 17 quantity words exactly
    twice, with the predicate-quantifier pairing and the trial order
    randomized per participant.

    ASSUMPTION: the paper only specifies that both argument types are
    generated "randomly for each quantity word" without fixing the
    predicate-quantifier pairing per participant, so this simulator pairs each
    (predicate, direction) slot with a shuffled pool in which each quantity
    word appears exactly twice. The response token mapping is fixed (A = valid,
    B = invalid), so no per-participant randomization is needed.

    The DataFrame matches exp3.csv minus the ``rt`` column.
    """

    def __init__(self):
        self.name = "vantiel_2021_probabilistic_exp3"
        self.strong = dict(STRONG)
        self.quantifiers = list(QUANTIFIERS)

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        # 17 predicates x 2 directions = 34 slots; 17 quantifiers x 2 = 34.
        slots = [(weak, d) for weak in self.strong
                 for d in ("strong_to_weak", "weak_to_strong")]
        for participant in tqdm(range(num_simulations)):
            prompt = INSTRUCTIONS
            order = np.random.permutation(len(slots)).tolist()
            quants = list(self.quantifiers) * 2
            np.random.shuffle(quants)
            for trial, idx in enumerate(order):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                weak, direction = slots[idx]
                strong = self.strong[weak]
                q = quants[trial]
                if direction == "strong_to_weak":
                    premise, conclusion = strong, weak
                else:
                    premise, conclusion = weak, strong
                prompt += (f"Argument: '{q} of the people {premise}. Therefore, "
                            f"{q} of the people {conclusion}.' "
                            f"You judge it [HUMAN_RESPONSE]")
                letter = agent(prompt, choice_options=["A", "B"])
                response = 1 if letter == "A" else 0
                prompt += f"{letter}[/HUMAN_RESPONSE] (A = valid, B = invalid).\n"
                rows.append({"participant_id": participant, "trial": trial,
                             "response": response, "condition": direction,
                             "quantifier": q, "predicate": weak})
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "condition", "quantifier",
            "predicate",
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

    task = Monotonicity()
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