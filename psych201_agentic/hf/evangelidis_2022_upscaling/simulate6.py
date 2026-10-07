# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp6 (Study 6) of ``Hugging-Brain/evangelidis_2022_upscaling``,
format-identical to the repo's ``transcripts6.jsonl``.

``uv run simulate6.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import json

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp6).
S6_STORY = {
    "backpack": "Imagine that you consider buying a backpack.",
    "speaker": "Imagine that you consider buying a Bluetooth speaker.",
    "harddrive": "Imagine that you consider buying an external hard drive.",
    "hotel": "Imagine that you are searching for a hotel room for your upcoming "
             "summer holidays.",
    "tv": "Suppose you consider buying a new TV. You pass by an electronics store "
          "that is having a one-day clearance sale.",
}
# stimulus -> (HF attr, HD attr, decoy attr); each attr = (quality, price)
S6_ATTRS = {
    "backpack": (("capacity 30 L", "$29.99"), ("capacity 40 L", "$39.99"),
                 ("capacity 30 L", "$39.99")),
    "speaker": (("Amazon rating 3.5 out of 5 stars", "$29.99"),
                ("Amazon rating 4.4 out of 5 stars", "$59.99"),
                ("Amazon rating 3.5 out of 5 stars", "$59.99")),
    "harddrive": (("capacity 1TB", "$39.99"), ("capacity 2TB", "$79.99"),
                  ("capacity 1TB", "$79.99")),
    "hotel": (("hotel rating 3-star", "$79 per night"),
              ("hotel rating 4-star", "$109 per night"),
              ("hotel rating 3-star", "$109 per night")),
    "tv": (("resolution 1920x1080", "$299"),
           ("resolution 3840x2160", "$599"),
           ("resolution 1920x1080", "$599")),
}
STIMULI = ["backpack", "speaker", "harddrive", "hotel", "tv"]
CONDITIONS = ["two_options", "three_options"]
DECOY_LOCS = ["next_to_hd", "next_to_hf"]


class UpscalingStudy6:
    """Study 6 of Evangelidis, Levav & Simonson (2022), "The upscaling effect",
    JCR 50(3) 492-509.

    Design (Study 6, p. 504): participants were randomly assigned to one of the
    2 (choice set: 2 vs 3 options) x 2 (decoy location: next to HD vs next to HF) x
    5 (choice problem: backpacks, Bluetooth speakers, external hard drives, hotels,
    TVs) between-participants conditions. Each problem offers an HD and an HF option
    (text attributes: price + a quality attribute); the decoy (C) is always added in
    the three-option condition. When the decoy is next to the HD option, the HF
    option is alternative A and the HD option B; when next to HF, the HD option is A
    and the HF option B. A "search for other options" no-choice is always available.

    ASSUMPTION: the CSV gives no between-subject probabilities, so condition,
    stimulus and decoy_loc are assigned uniformly at random, matching the ~50/50 and
    ~20%-per-stimulus frequencies in exp6.csv.

    The DataFrame matches exp6.csv minus the demographics ``age``/``gender``.
    """
    def __init__(self):
        self.name = "evangelidis_2022_upscaling_exp6"
        self.stimuli = STIMULI
        self.conditions = CONDITIONS
        self.decoy_locs = DECOY_LOCS

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for p in tqdm(range(num_simulations)):
            condition = str(np.random.choice(self.conditions))
            n = 3 if condition == "two_options" else 4  # + no-choice slot
            stim = str(np.random.choice(self.stimuli))
            decoy_loc = str(np.random.choice(self.decoy_locs))
            hf_attr, hd_attr, decoy_attr = S6_ATTRS[stim]
            if decoy_loc == "next_to_hd":
                a, b = hf_attr, hd_attr
            else:  # next to HF -> HD option is A
                a, b = hd_attr, hf_attr
            text = (f"{S6_STORY[stim]} You have the following options: Brand A, "
                    f"{a[0]}, price {a[1]}; Brand B, {b[0]}, price {b[1]}")
            if n == 4:
                text += (f"; Brand C, {decoy_attr[0]}, price {decoy_attr[1]}")
            text += (". What would you do? Press the letter of the option you choose, "
                     "or S to search for other options. You press [HUMAN_RESPONSE]")
            prompt = text
            tokens = [chr(ord("A") + i) for i in range(n - 1)] + ["S"]
            token = agent(prompt, choice_options=tokens)
            response = n - 1 if token == "S" else ord(token) - ord("A")
            text += f"{token}[/HUMAN_RESPONSE]."
            rows.append({
                "participant_id": f"P{p:03d}", "trial": 0, "condition": condition,
                "stimulus": stim, "decoy_loc": decoy_loc, "n_options": n,
                "choice_set": json.dumps([f"option_{i}" for i in range(n)]),
                "response": response, "deferral": int(response == n - 1),
            })
            prompts.append(text)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "condition", "stimulus", "decoy_loc",
            "n_options", "choice_set", "response", "deferral",
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

    task = UpscalingStudy6()
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