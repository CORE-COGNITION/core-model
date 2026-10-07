# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp2 (Study 3) of ``Hugging-Brain/evangelidis_2022_upscaling``,
format-identical to the repo's ``transcripts2.jsonl``.

``uv run simulate2.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import json

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp2).
S3_HD_OPT = ("Hotel", "price $119 per night", "hotel rating 4-star")
S3_HF_OPT = ("Hotel", "price $89 per night", "hotel rating 3-star")
S3_DECOY = ("Hotel", "price $119 per night", "hotel rating 3-star")
VERSIONS = ["v1", "v2"]
CONDITIONS = ["two_options", "three_options"]


class UpscalingStudy3:
    """Study 3 of Evangelidis, Levav & Simonson (2022), "The upscaling effect",
    JCR 50(3) 492-509.

    Design (Study 3, p. 501): a single between-participants hotel choice between an
    HD (Hotel, 4-star, $119/night) and an HF (Hotel, 3-star, $89/night) option, with
    a "search for other options" no-choice. Half see a two-option set, half see a
    symmetrically dominated decoy (Hotel C, 3-star, $119/night) added. The A/B
    labels are counterbalanced: in v1 the HF option is A and the HD option B; in v2
    the HD option is A and the HF option B. Before the choice participants give a
    free-text explanation of their reasons.

    ASSUMPTION: the CSV gives no between-subject probabilities, so condition and
    version are assigned uniformly at random, matching the ~50/50 frequencies in
    exp2.csv.

    The DataFrame matches exp2.csv minus the demographics ``age``/``gender`` and the
    rater-coded dummies ``SimilarPriceBetterRating``/``SimilarRatingLowerPrice``/
    ``Justifiability``, which a text simulator cannot produce.
    """
    def __init__(self):
        self.name = "evangelidis_2022_upscaling_exp2"
        self.versions = VERSIONS
        self.conditions = CONDITIONS

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for p in tqdm(range(num_simulations)):
            condition = str(np.random.choice(self.conditions))
            n = 3 if condition == "two_options" else 4  # + no-choice slot
            ver = str(np.random.choice(self.versions))
            hd, hf, decoy = S3_HD_OPT, S3_HF_OPT, S3_DECOY
            letter_a = hf if ver == "v1" else hd
            letter_b = hd if ver == "v1" else hf
            parts = [f"Hotel A: {letter_a[1]}, {letter_a[2]}",
                     f"Hotel B: {letter_b[1]}, {letter_b[2]}"]
            if n == 4:
                parts.append(f"Hotel C: {decoy[1]}, {decoy[2]}")
            prompt = ("Imagine that you are searching for a hotel room for your "
                      f"upcoming summer holidays. In your search, you find the "
                      f"following options: {'; '.join(parts)}.\n")
            prompt += ("Before making a choice, please explain in a few sentences what "
                       "motivates your decision and what reasons or factors motivate "
                       "your preference for one (or none) of these options. You "
                       "write: [HUMAN_RESPONSE]")
            expl = agent(prompt, choice_options=None)
            prompt += f"{expl}[/HUMAN_RESPONSE]\n"
            letters = [chr(ord("A") + i) for i in range(n - 1)] + ["S"]
            prompt += ("What would you do? Press the letter of the option you choose, "
                       "or S to search for other options. You press [HUMAN_RESPONSE]")
            token = agent(prompt, choice_options=letters)
            response = n - 1 if token == "S" else ord(token) - ord("A")
            prompt += f"{token}[/HUMAN_RESPONSE]."
            rows.append({
                "participant_id": f"P{p:03d}", "trial": 0, "condition": condition,
                "version": ver, "n_options": n,
                "choice_set": json.dumps([f"option_{i}" for i in range(n)]),
                "response": response, "deferral": int(response == n - 1),
                "explanation": expl,
            })
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "condition", "version", "n_options",
            "choice_set", "response", "deferral", "explanation",
        ])
        return df, prompts


def _random_agent(prompt, choice_options=None):
    if choice_options is None:
        return "I would consider both price and rating before deciding."
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

    task = UpscalingStudy3()
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