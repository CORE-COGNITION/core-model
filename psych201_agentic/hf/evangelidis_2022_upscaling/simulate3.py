# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp3 (Study 4) of ``Hugging-Brain/evangelidis_2022_upscaling``,
format-identical to the repo's ``transcripts3.jsonl``.

``uv run simulate3.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import json

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp3).
S4_HD_ATTR = ("$59.99", "Amazon rating 4.3 out of 5 stars")
S4_HF_ATTR = ("$29.99", "Amazon rating 3.5 out of 5 stars")
S4_DECOY_ATTR = ("$59.99", "Amazon rating 3.5 out of 5 stars")
VERSIONS = ["v1", "v2"]
CONDITIONS = ["two_options", "three_options"]


class UpscalingStudy4:
    """Study 4 of Evangelidis, Levav & Simonson (2022), "The upscaling effect",
    JCR 50(3) 492-509.

    Design (Study 4, pp. 501-502): a single between-participants Bluetooth speaker
    choice between an HD (Brand B, 4.3 stars, $59.99) and an HF (Brand A, 3.5 stars,
    $29.99) option, with a "search for other options" no-choice. Half see a
    two-option set, half see a symmetrically dominated decoy (Brand C, 3.5 stars,
    $59.99) added. The A/B labels are counterbalanced (version v1/v2). Participants
    rate how easy it is to justify choosing each brand (1-7) and give a free-text
    explanation; the justification block comes before the choice for half the
    participants (justif_before_choice = 1) and after for the rest.

    ASSUMPTION: the CSV gives no between-subject probabilities, so condition,
    version and justification order are assigned uniformly at random, matching the
    ~50/50 frequencies in exp3.csv.

    The DataFrame matches exp3.csv minus the demographics ``age``/``gender``.
    """
    def __init__(self):
        self.name = "evangelidis_2022_upscaling_exp3"
        self.versions = VERSIONS
        self.conditions = CONDITIONS

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for p in tqdm(range(num_simulations)):
            condition = str(np.random.choice(self.conditions))
            n = 3 if condition == "two_options" else 4  # + no-choice slot
            ver = str(np.random.choice(self.versions))
            just_before = int(np.random.rand() < 0.5)
            a_price, a_qual = (S4_HF_ATTR if ver == "v1" else S4_HD_ATTR)
            b_price, b_qual = (S4_HD_ATTR if ver == "v1" else S4_HF_ATTR)

            prompt = ("Imagine that you consider buying a Bluetooth speaker. In your "
                      "search, you find the following options: Brand A, " + a_qual +
                      ", price " + a_price + "; Brand B, " + b_qual + ", price " +
                      b_price)
            if n == 4:
                prompt += ("; Brand C, " + S4_DECOY_ATTR[1] + ", price " +
                           S4_DECOY_ATTR[0])
            prompt += ".\n"

            def justification_block(letter):
                prompt_inner = (f"How easy is it to justify choosing {letter}? Rate "
                                "from 1 (not at all easy) to 7 (very easy). You rate "
                                "[HUMAN_RESPONSE]")
                rating = int(agent(prompt + prompt_inner,
                                   choice_options=[str(i) for i in range(1, 8)]))
                prompt_inner += (f"{rating}[/HUMAN_RESPONSE]. Please explain in a few "
                                 f"sentences how choice of {letter} could be "
                                 "justified. You write: [HUMAN_RESPONSE]")
                expl = agent(prompt + prompt_inner, choice_options=None)
                return prompt_inner + f"{expl}[/HUMAN_RESPONSE]\n", rating, expl

            just_blocks = {}
            if just_before == 1:
                blockA, jA, eA = justification_block("Brand A")
                prompt += blockA
                just_blocks = {"JustifA": jA, "JustifB": None, "ExplA": eA, "ExplB": None}
                blockB, jB, eB = justification_block("Brand B")
                prompt += blockB
                just_blocks = {"JustifA": jA, "JustifB": jB, "ExplA": eA, "ExplB": eB}

            letters = [chr(ord("A") + i) for i in range(n - 1)] + ["S"]
            prompt += ("What would you do? Press the letter of the option you choose, "
                       "or S to search for other options. You press [HUMAN_RESPONSE]")
            token = agent(prompt, choice_options=letters)
            response = n - 1 if token == "S" else ord(token) - ord("A")
            prompt += f"{token}[/HUMAN_RESPONSE]."

            if just_before == 0:
                prompt += "\n"
                blockA, jA, eA = justification_block("Brand A")
                prompt += blockA
                blockB, jB, eB = justification_block("Brand B")
                prompt += blockB.rstrip()
                just_blocks = {"JustifA": jA, "JustifB": jB, "ExplA": eA, "ExplB": eB}

            prompt = prompt.strip()
            rows.append({
                "participant_id": f"P{p:03d}", "trial": 0, "condition": condition,
                "version": ver, "n_options": n,
                "choice_set": json.dumps([f"option_{i}" for i in range(n)]),
                "response": response, "deferral": int(response == n - 1),
                "JustifA": just_blocks["JustifA"], "JustifB": just_blocks["JustifB"],
                "ExplA": just_blocks["ExplA"], "ExplB": just_blocks["ExplB"],
                "justif_before_choice": just_before,
            })
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "condition", "version", "n_options",
            "choice_set", "response", "deferral", "JustifA", "JustifB", "ExplA",
            "ExplB", "justif_before_choice",
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

    task = UpscalingStudy4()
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