# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 (Study 1) of ``Hugging-Brain/evangelidis_2022_upscaling``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import json

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp0).
S1_STORY = {
    "backpack": "Imagine that you consider buying a backpack.",
    "speaker": "Imagine that you consider buying a Bluetooth speaker.",
    "harddrive": "Imagine that you consider buying an external hard drive.",
    "hotel": "Imagine that you are searching for a hotel room for your upcoming "
             "summer holidays.",
    "tv": "Suppose you consider buying a new TV. You pass by an electronics store "
          "that is having a one-day clearance sale.",
}
# stimulus -> {index: (label, quality attribute, price)}
S1_OPTS = {
    "backpack": {0: ("Backpack A", "capacity 30 L", "$29.99"),
                 1: ("Backpack B", "capacity 40 L", "$39.99"),
                 2: ("Backpack C", "capacity 30 L", "$39.99")},
    "speaker": {0: ("Brand A", "Amazon rating 3.6 out of 5 stars", "$39.99"),
                1: ("Brand B", "Amazon rating 4.5 out of 5 stars", "$69.99"),
                2: ("Brand C", "Amazon rating 3.6 out of 5 stars", "$69.99")},
    "harddrive": {0: ("Brand A", "capacity 1TB", "$39.99"),
                  1: ("Brand B", "capacity 2TB", "$79.99"),
                  2: ("Brand C", "capacity 1TB", "$79.99")},
    "hotel": {0: ("Hotel A", "hotel rating 3-star", "$79 per night"),
              1: ("Hotel B", "hotel rating 4-star", "$109 per night"),
              2: ("Hotel C", "hotel rating 3-star", "$109 per night")},
    "tv": {0: ("Brand A", "resolution 1920x1080, picture quality good", "$199"),
           1: ("Brand B", "resolution 3840x2160, picture quality excellent", "$399"),
           2: ("Brand C", "resolution 1920x1080, picture quality good", "$399")},
}
STIMULI = ["backpack", "speaker", "harddrive", "hotel", "tv"]
CONDITIONS = ["two_options", "three_options"]


class UpscalingStudy1:
    """Study 1 of Evangelidis, Levav & Simonson (2022), "The upscaling effect",
    JCR 50(3) 492-509.

    Design (Study 1, pp. 498-499, Table 1): a single between-participants choice
    between a high-desirability (HD) and a high-feasibility (HF) option described
    by text attributes (price + a quality attribute), drawn from five product
    categories. Half the participants see a two-option set, half see the same two
    options plus a symmetrically dominated decoy (C); a "search for other options"
    no-choice is always available. Participants are randomly assigned to one of the
    2 (choice set) x 5 (choice problem) conditions.

    ASSUMPTION: the CSV gives no between-subject probabilities, so the simulator
    assigns condition and stimulus uniformly at random, matching the ~50/50 and
    ~20%-per-stimulus frequencies in exp0.csv.

    The DataFrame matches exp0.csv minus ``code`` (a Qualtrics source code) and the
    demographics ``age``/``gender``, which a text simulator cannot produce.
    """
    def __init__(self):
        self.name = "evangelidis_2022_upscaling_exp0"
        self.stimuli = STIMULI
        self.conditions = CONDITIONS

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for p in tqdm(range(num_simulations)):
            condition = str(np.random.choice(self.conditions))
            n = 3 if condition == "two_options" else 4  # + no-choice slot
            stim = str(np.random.choice(self.stimuli))
            opts = S1_OPTS[stim]
            opts_list = "; ".join(f"{opts[i][0]}, {opts[i][1]}, price {opts[i][2]}"
                                  for i in range(n - 1))
            prompt = (f"{S1_STORY[stim]} You have the following options: {opts_list}. "
                      "What would you do? Press the letter of the option you choose, or "
                      "S to search for other options.\n")
            letters = [chr(ord("A") + i) for i in range(n - 1)] + ["S"]
            prompt += "You press [HUMAN_RESPONSE]"
            token = agent(prompt, choice_options=letters)
            response = n - 1 if token == "S" else ord(token) - ord("A")
            prompt += f"{token}[/HUMAN_RESPONSE]."
            deferral = int(response == n - 1)
            rows.append({
                "participant_id": f"P{p:03d}", "trial": 0, "condition": condition,
                "stimulus": stim, "n_options": n,
                "choice_set": json.dumps([f"option_{i}" for i in range(n)]),
                "response": response, "deferral": deferral,
            })
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "condition", "stimulus", "n_options",
            "choice_set", "response", "deferral",
        ])
        return df, prompts


def _random_agent(prompt, choice_options=None):
    if choice_options is None:
        return "I would weigh both price and quality before deciding."
    return str(np.random.choice(choice_options))


def main():
    parser = argparse.ArgumentParser(
        description="Smoke-test this simulator with a uniform-random agent.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3, help="number of simulated participants (default: 3)")
    parser.add_argument("--max-chars", type=int, default=None, help="stop each participant at the block boundary at/past this many chars")
    parser.add_argument("--seed", type=int, default=None, help="numpy random seed, for reproducible runs")
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    task = UpscalingStudy1()
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