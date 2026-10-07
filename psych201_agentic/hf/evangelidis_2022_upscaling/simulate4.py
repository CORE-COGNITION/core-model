# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp4 (Study 5) of ``Hugging-Brain/evangelidis_2022_upscaling``,
format-identical to the repo's ``transcripts4.jsonl``.

``uv run simulate4.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import json

import numpy as np
import pandas as pd
from tqdm import tqdm

VERSIONS = ["v1", "v2"]
CONDITIONS = ["two_options", "three_options"]
HD_PRICES = ["high", "low"]


class UpscalingStudy5:
    """Study 5 of Evangelidis, Levav & Simonson (2022), "The upscaling effect",
    JCR 50(3) 492-509.

    Design (Study 5, pp. 503-504): a hard drive choice. Participants are randomly
    assigned to one of the 2 (choice set: 2 vs 3 options) x 2 (version: A/B label
    counterbalance) x 2 (HD price: high $79.99 vs low $42.99) between-participants
    conditions. The HD option (Brand B) is 4TB at the HD price; the HF option
    (Brand A) is 2TB at $39.99; the decoy (Brand C) is 2TB at the HD price (only in
    the three-option condition). A "search for other options" no-choice is always
    available.

    ASSUMPTION: the CSV gives no between-subject probabilities, so condition,
    version and hd_price are assigned uniformly at random, matching the ~50/50
    frequencies in exp4.csv.

    The DataFrame matches exp4.csv minus the demographics ``age``/``gender``.
    """
    def __init__(self):
        self.name = "evangelidis_2022_upscaling_exp4"
        self.versions = VERSIONS
        self.conditions = CONDITIONS
        self.hd_prices = HD_PRICES

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for p in tqdm(range(num_simulations)):
            condition = str(np.random.choice(self.conditions))
            n = 3 if condition == "two_options" else 4  # + no-choice slot
            ver = str(np.random.choice(self.versions))
            hd_price = str(np.random.choice(self.hd_prices))
            hp = "$79.99" if hd_price == "high" else "$42.99"
            hf, hd = ("capacity 2TB", "$39.99"), ("capacity 4TB", hp)
            a, b = (hf if ver == "v1" else hd), (hd if ver == "v1" else hf)
            text = ("Imagine that you consider buying an external hard drive. You "
                    f"have the following options: Brand A, {a[0]}, price {a[1]}; "
                    f"Brand B, {b[0]}, price {b[1]}")
            if n == 4:
                text += f"; Brand C, capacity 2TB, price {hp}"
            text += (". What would you do? Press the letter of the option you "
                     "choose, or S to search for other options. You press "
                     "[HUMAN_RESPONSE]")
            prompt = text
            letters = [chr(ord("A") + i) for i in range(n - 1)] + ["S"]
            token = agent(prompt, choice_options=letters)
            response = n - 1 if token == "S" else ord(token) - ord("A")
            prompt += f"{token}[/HUMAN_RESPONSE]."
            rows.append({
                "participant_id": f"P{p:03d}", "trial": 0, "condition": condition,
                "version": ver, "hd_price": hd_price, "n_options": n,
                "choice_set": json.dumps([f"option_{i}" for i in range(n)]),
                "response": response, "deferral": int(response == n - 1),
            })
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "condition", "version", "hd_price",
            "n_options", "choice_set", "response", "deferral",
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

    task = UpscalingStudy5()
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