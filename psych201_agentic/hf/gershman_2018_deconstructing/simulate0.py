# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/gershman_2018_deconstructing``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp0), with the letter slots kept.
INSTRUCTIONS = (
    "Welcome. In this task you have a choice between two slot machines, represented by "
    "colored buttons. When you choose the left (variable) machine, you will win or lose "
    "points. The left machine will not always give you the same points, but it will tend to "
    "give points around its average value. When you choose the right (fixed) machine, you will always "
    "get 0 points. Your goal is to choose the slot machine that will give you the most "
    "points. After making your choice, you will receive feedback about the outcome. You "
    "will play 20 games, each with a different left (variable) slot machine (the right, "
    "fixed machine will always stay the same). Each game will consist of 10 trials. "
    "Press {aid} to choose the left (variable) machine and {bid} to choose the right "
    "(fixed) machine.")


class TwoArmedBandit:
    """Two-armed bandit, Experiment 1 of Gershman (2018), "Deconstructing the
    human algorithms for exploration", Cognition, 173, 34-42.

    Design (3.2 Stimuli and Procedure, p. 36): 20 games ("blocks") of 10 free
    choices between arm 1 (left, variable) and arm 2 (right, fixed). Arm 1's
    mean payout mu1 is redrawn each game from a zero-mean Gaussian; choosing it
    pays Gaussian noise around mu1. Arm 2 always pays exactly 0 points.

    ASSUMPTION: the shipped data disagree with the paper's stated variances
    (variance 10 for both the mean distribution and the reward noise) -- across
    the 900 games in exp0.csv, mu1 has variance ~1.13 and the arm-1 reward
    residuals ~1.09, both integer-valued (consistent with rounded unit-variance
    Gaussians). Per the data-authoritative rule this simulator uses the
    measured parameters: mu1 = round(N(0, 1)); arm-1 reward = round(N(mu1, 1));
    arm-2 reward = 0.

    The DataFrame matches exp0.csv minus ``rt``.
    """

    def __init__(self):
        self.name = "gershman_2018_deconstructing_exp0"
        self.num_games = 20        # fresh bandit (new mu1) each game
        self.num_trials = 10       # free choices per game
        self.mu_sd = 1.0           # mu1 ~ round(N(0, mu_sd)); mu2 fixed at 0
        self.reward_sd = 1.0       # arm-1 reward ~ round(N(mu1, reward_sd))

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            # per-participant A/B mapping, as in build_jsonl.py; aid = arm 1 (response 0)
            aid, bid = ("A", "B") if np.random.rand() < 0.5 else ("B", "A")
            prompt = INSTRUCTIONS.format(aid=aid, bid=bid)
            for game in range(self.num_games):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                mu1 = int(np.round(np.random.normal(0.0, self.mu_sd)))
                prompt += f"\nGame {game + 1}: a new pair of slot machines appears."
                for trial in range(self.num_trials):
                    prompt += "\nYou press [HUMAN_RESPONSE]"
                    letter = agent(prompt, choice_options=[aid, bid])
                    response = 0 if letter == aid else 1
                    reward = (int(np.round(np.random.normal(mu1, self.reward_sd)))
                              if response == 0 else 0)
                    prompt += f"{letter}[/HUMAN_RESPONSE]. You receive {reward} points."
                    rows.append({
                        "participant_id": participant, "task_id": game, "trial": trial,
                        "mu1": mu1, "mu2": 0, "choice": response + 1,
                        "response": response, "reward": reward,
                    })
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "task_id", "trial", "mu1", "mu2", "choice", "response", "reward",
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

    task = TwoArmedBandit()
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