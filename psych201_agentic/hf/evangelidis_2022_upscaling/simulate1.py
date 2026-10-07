# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 (Study 2) of ``Hugging-Brain/evangelidis_2022_upscaling``,
format-identical to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a random-armed agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import json

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp1).
S2_OPTS = {0: ("Brand A", "capacity 2TB", "$39.99"),
           1: ("Brand B", "capacity 4TB", "$79.99"),
           2: ("Brand C", "capacity 2TB", "$79.99")}
DOM = {"A": 1, "B": 2, "AB": 3}
SC_COLS = [f"SelfConstrual_{k}" for k in range(1, 11)]


class UpscalingStudy2:
    """Study 2 of Evangelidis, Levav & Simonson (2022), "The upscaling effect",
    JCR 50(3) 492-509.

    Design (Study 2, pp. 499-500): a within-subject repeated-measures design on
    hard drives. Every participant first makes a two-option choice between Brand A
    (HF, 2TB / $39.99) and Brand B (HD, 4TB / $79.99) with a "search for other
    options" no-choice; then rates their liking of each brand on two independent
    20-point slider scales; then completes a 10-item self-construal scale
    (Singelis 1994, 1-7, filler task); then sees the same two options plus the
    decoy Brand C (2TB / $79.99) and makes a second choice; then indicates which
    option is clearly better than C (A, B, or both, AB).

    ASSUMPTION: the transcript encodes all 10 self-construal responses on one
    line; the simulator asks the agent for each rating. No between-subject factor
    is varied in Study 2, so every simulated participant sees the same options.

    The DataFrame matches exp1.csv minus the demographics ``age``/``gender``.
    """
    def __init__(self):
        self.name = "evangelidis_2022_upscaling_exp1"
        self.n0 = 3  # two-option set + no-choice slot
        self.n1 = 4  # three-option set + no-choice slot

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        lab0, q0, p0 = S2_OPTS[0]
        lab1, q1, p1 = S2_OPTS[1]
        lab2, q2, p2 = S2_OPTS[2]

        for p in tqdm(range(num_simulations)):
            prompt = ("Imagine that you consider buying an external hard drive. You "
                      f"have the following options: {lab0}, {q0}, price {p0}; {lab1}, "
                      f"{q1}, price {p1}. What would you do? Press the letter of the "
                      "option you choose, or S to search for other options.\n")
            prompt += "You press [HUMAN_RESPONSE]"
            c0 = agent(prompt, choice_options=["A", "B", "S"])
            r0 = self.n0 - 1 if c0 == "S" else ord(c0) - ord("A")
            prompt += f"{c0}[/HUMAN_RESPONSE].\n"

            prompt += ("Independently of your choice, how much do you like each brand? "
                       "Rate from 1 (not at all) to 20 (very much). You rate "
                       f"{lab0} [HUMAN_RESPONSE]")
            liking1 = int(agent(prompt, choice_options=[str(i) for i in range(1, 21)]))
            prompt += f"{liking1}[/HUMAN_RESPONSE] and you rate {lab1} [HUMAN_RESPONSE]"
            liking2 = int(agent(prompt, choice_options=[str(i) for i in range(1, 21)]))
            prompt += f"{liking2}[/HUMAN_RESPONSE].\n"

            prompt += ("Next you complete a 10-item self-construal scale. For each "
                       "statement, rate how much you agree from 1 (strongly disagree) "
                       "to 7 (strongly agree): you respond ")
            sc = []
            for k in range(1, 11):
                prompt += f"item {k} [HUMAN_RESPONSE]"
                v = int(agent(prompt, choice_options=[str(i) for i in range(1, 8)]))
                sc.append(v)
                prompt += f"{v}[/HUMAN_RESPONSE] "
            prompt = prompt.rstrip() + ".\n"

            prompt += (f"Now, an additional option is added to the set: {lab2}, {q2}, "
                       f"price {p2}. The options are now {lab0}, {lab1}, and {lab2}. "
                       "What would you do? Press the letter of the option you choose, "
                       "or S to search for other options. You press [HUMAN_RESPONSE]")
            c1 = agent(prompt, choice_options=["A", "B", "C", "S"])
            r1 = self.n1 - 1 if c1 == "S" else ord(c1) - ord("A")
            prompt += f"{c1}[/HUMAN_RESPONSE].\n"

            prompt += (f"Which option is clearly better than {lab2}? Press A if only "
                       f"{lab0}, B if only {lab1}, or AB if both are better. You press "
                       "[HUMAN_RESPONSE]")
            dom_token = agent(prompt, choice_options=["A", "B", "AB"])
            dom = DOM[dom_token]
            prompt += f"{dom_token}[/HUMAN_RESPONSE]."
            prompts.append(prompt)

            row0 = {
                "participant_id": f"P{p:03d}", "trial": 0, "condition": "two_options",
                "n_options": self.n0,
                "choice_set": json.dumps([f"option_{i}" for i in range(self.n0)]),
                "response": r0, "deferral": int(r0 == self.n0 - 1),
                "Liking_1": liking1, "Liking_2": liking2, "BeliefsDom": dom,
                **{c: sc[k - 1] for k, c in enumerate(SC_COLS, 1)},
            }
            row1 = {
                "participant_id": f"P{p:03d}", "trial": 1, "condition": "three_options",
                "n_options": self.n1,
                "choice_set": json.dumps([f"option_{i}" for i in range(self.n1)]),
                "response": r1, "deferral": int(r1 == self.n1 - 1),
                "Liking_1": liking1, "Liking_2": liking2, "BeliefsDom": dom,
                **{c: sc[k - 1] for k, c in enumerate(SC_COLS, 1)},
            }
            rows.append(row0)
            rows.append(row1)

        cols = ["participant_id", "trial", "condition", "n_options", "choice_set",
                "response", "deferral", "Liking_1", "Liking_2", "BeliefsDom", *SC_COLS]
        df = pd.DataFrame(rows, columns=cols)
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

    task = UpscalingStudy2()
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