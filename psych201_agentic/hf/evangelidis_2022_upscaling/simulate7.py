# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp7 (Study 7) of ``Hugging-Brain/evangelidis_2022_upscaling``,
format-identical to the repo's ``transcripts7.jsonl``.

``uv run simulate7.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import json

import numpy as np
import pandas as pd
from tqdm import tqdm

CONDITIONS = ["two_options", "three_options"]
PRESENTATIONS = ["same", "different"]


class UpscalingStudy7:
    """Study 7 of Evangelidis, Levav & Simonson (2022), "The upscaling effect",
    JCR 50(3) 492-509.

    Design (Study 7, p. 505): participants were randomly assigned to one of the
    2 (choice set: two vs three options) x 2 (presentation mode: same page vs
    different pages) between-participants conditions of a hard drive choice. They
    view the options in text: Brand A ($39.99, 2TB, HF), Brand B ($79.99, 4TB, HD),
    and (in the three-option condition) Brand C ($79.99, 2TB, decoy). All options
    are presented either on one page or on separate pages, after which they make a
    choice; a "search for other options" no-choice is available.

    ASSUMPTION: the CSV gives no between-subject probabilities, so condition and
    presentation are assigned uniformly at random, matching the ~50/50 frequencies
    in exp7.csv.

    The DataFrame matches exp7.csv minus the demographics ``age``/``gender``.
    """
    def __init__(self):
        self.name = "evangelidis_2022_upscaling_exp7"
        self.conditions = CONDITIONS
        self.presentations = PRESENTATIONS

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for p in tqdm(range(num_simulations)):
            condition = str(np.random.choice(self.conditions))
            n = 3 if condition == "two_options" else 4  # + no-choice slot
            presentation = str(np.random.choice(self.presentations))
            pres = ("At the same time, on one page" if presentation == "same"
                    else "On different pages (each shown separately)")
            text = ("Imagine that you consider buying an external hard drive. "
                    "Brand A is priced at $39.99 and has a storage capacity of 2TB. "
                    "Brand B is priced at $79.99 and has a storage capacity of 4TB.")
            if n == 4:
                text += (" Brand C is priced at $79.99 and has a storage capacity of "
                         "2TB.")
            text += (f" {pres}, you view these options and then make a choice. What "
                     "would you do? Press the letter of the option you choose, or S "
                     "to search for other options. You press [HUMAN_RESPONSE]")
            prompt = text
            tokens = [chr(ord("A") + i) for i in range(n - 1)] + ["S"]
            token = agent(prompt, choice_options=tokens)
            response = n - 1 if token == "S" else ord(token) - ord("A")
            text += f"{token}[/HUMAN_RESPONSE]."
            rows.append({
                "participant_id": f"P{p:03d}", "trial": 0, "condition": condition,
                "presentation": presentation, "n_options": n,
                "choice_set": json.dumps([f"option_{i}" for i in range(n)]),
                "response": response, "deferral": int(response == n - 1),
            })
            prompts.append(text)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "condition", "presentation", "n_options",
            "choice_set", "response", "deferral",
        ])
        return df, prompts


def _random_agent(prompt, choice_options=None):
    if choice_options is None:
        return "I would weigh both capacity and price before deciding."
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

    task = UpscalingStudy7()
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