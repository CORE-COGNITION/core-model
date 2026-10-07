# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp3 of ``Hugging-Brain/schulz_2020_finding``,
format-identical to the repo's ``transcripts3.jsonl``.

``uv run simulate3.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (BASE_INSTR).
INSTRUCTIONS = (
    "In this game you play 30 rounds of a slot-machine task. Each round, eight boxes are "
    "arranged left to right and labeled with the keys you press to choose them: A, S, D, F, "
    "J, K, L, and ; (semicolon), leftmost to rightmost. Each round has 10 trials. On each "
    "trial you press one key to sample that box, and you then see how many points that box "
    "gave you this time. Your goal is to gain as many points as possible. After each round "
    "the game resets: the same keys can now give different points, so treat every round afresh."
)
KEYS = ["A", "S", "D", "F", "J", "K", "L", ";"]


def _linear_fn(rng, neg):
    fmin = rng.uniform(2.0, 10.0)
    fmax = rng.uniform(40.0, 48.0)
    return [fmin + ((7 - i if neg else i) / 7.0) * (fmax - fmin) for i in range(8)]


def _random_fn(rng):
    fn = _linear_fn(rng, neg=rng.random() < 0.5)
    rng.shuffle(fn)
    return fn


class DynamicsBandit:
    """Experiment 4 of Schulz, Franklin & Gershman (2020), "Finding structure in
    multi-armed bandits", Cognitive Psychology, 119, 101261 (bioRxiv 432534).

    Design (Experiment 4, Design/Procedure, pp. 26-27): two between-subjects
    groups. SRS: rounds 1-10 structured, 11-20 random, 21-30 structured; RSR:
    rounds 1-10 random, 11-20 structured, 21-30 random. A structured block draws
    5 increasing and 5 decreasing linear functions (pool of Fig. 3) in random
    order; a random block uses shuffled linear functions, exactly as Experiment 1.

    ASSUMPTION: exp3.csv records no group/condition column (see README), so the
    SRS/RSR assignment is not recoverable from the shipped data; this simulator
    assigns it at random per participant (50/50). eps ~ N(0, 0.3) per the
    observed within-round scatter (paper states N(0, 0.1)).

    The DataFrame matches exp3.csv.
    """

    def __init__(self):
        self.name = "schulz_2020_finding_exp3"
        self.num_rounds = 30
        self.num_trials = 10
        self.num_arms = 8
        self.noise_sd = 0.3

    def _round_condition(self, round_idx, srs):
        block = round_idx // 10
        structured = block == 0 if srs else block == 1   # SRS: 0,2 structured; RSR: 1
        return "structured" if structured else "random"

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            prompt = INSTRUCTIONS + "\n"
            rng = np.random.default_rng(participant)
            srs = rng.random() < 0.5
            for round_idx in range(self.num_rounds):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                if self._round_condition(round_idx, srs) == "structured":
                    fn = _linear_fn(rng, neg=(round_idx % 2 == 1))   # 5 pos / 5 neg in order
                else:
                    fn = _random_fn(rng)
                prompt += f"\nRound {round_idx + 1} of 30.\n"
                for trial in range(self.num_trials):
                    prompt += f"Trial {trial + 1}: You press [HUMAN_RESPONSE]"
                    key = agent(prompt, choice_options=KEYS)
                    response = KEYS.index(key)
                    reward = float(np.random.normal(fn[response], self.noise_sd))
                    prompt += f"{key}[/HUMAN_RESPONSE] and gain {round(reward, 2)} points.\n"
                    rows.append({
                        "participant_id": participant + 1, "task_id": round_idx,
                        "trial": trial, "response": response,
                        "round": round_idx + 1, "arm": response + 1, "reward": reward,
                    })
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "task_id", "trial", "response", "round", "arm", "reward",
        ])
        return df, prompts


def _random_agent(prompt, choice_options):
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

    task = DynamicsBandit()
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