# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 of ``Hugging-Brain/gershman_2018_deconstructing``,
format-identical to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp1), with the letter slots kept.
INSTRUCTIONS = (
    "Welcome. In this task you have a choice between two slot machines, represented by "
    "colored buttons. When you click one of the buttons, you will win or lose points. "
    "Choosing the same slot machine will not always give you the same points, but one slot "
    "machine is always better than the other. Your goal is to choose the slot machine that "
    "will give you the most points. After making your choice, you will receive feedback "
    "about the outcome. You will play 20 games, each with a different pair of slot "
    "machines. Each game will consist of 10 trials. Press {aid} to choose the left machine "
    "and {bid} to choose the right machine.")


class DualStochasticBandit:
    """Two-armed bandit, Experiment 2 of Gershman (2018), "Deconstructing the
    human algorithms for exploration", Cognition, 173, 34-42.

    Design (3.2 Stimuli and Procedure, p. 36): 20 games ("blocks") of 10 free
    choices. Both arms are stochastic: each game redraws both mean payouts
    independently from a zero-mean Gaussian, and choosing an arm pays Gaussian
    noise around that arm's mean.

    ASSUMPTION: the shipped data disagree with the paper's stated variances
    (mean distribution variance 100, reward noise variance 10) -- across the
    880 games in exp1.csv, the arm means have variance ~66 (rounded-normal MLE
    sigma ~8.1) and the reward residuals ~1.09 (sigma ~1), all integer-valued.
    Per the data-authoritative rule this simulator uses the measured
    parameters: mu1, mu2 = round(N(0, 8.1)); reward of the chosen arm =
    round(N(mu_selected, 1)). The two arm means are drawn independently
    (hypothesis confirmed: sample corr(mu1, mu2) ~ 0.02).

    The DataFrame matches exp1.csv minus ``rt``.
    """

    def __init__(self):
        self.name = "gershman_2018_deconstructing_exp1"
        self.num_games = 20        # fresh bandit (new mu1, mu2) each game
        self.num_trials = 10       # free choices per game
        self.mu_sd = 8.1           # mu1, mu2 ~ round(N(0, mu_sd)), independent
        self.reward_sd = 1.0       # reward of chosen arm ~ round(N(mu, reward_sd))

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            # per-participant A/B mapping, as in build_jsonl.py; aid = arm 1 (response 0)
            aid, bid = ("A", "B") if np.random.rand() < 0.5 else ("B", "A")
            prompt = INSTRUCTIONS.format(aid=aid, bid=bid)
            for game in range(self.num_games):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                mus = [int(np.round(np.random.normal(0.0, self.mu_sd)))
                       for _ in range(2)]
                mu1, mu2 = mus
                prompt += f"\nGame {game + 1}: a new pair of slot machines appears."
                for trial in range(self.num_trials):
                    prompt += "\nYou press [HUMAN_RESPONSE]"
                    letter = agent(prompt, choice_options=[aid, bid])
                    response = 0 if letter == aid else 1
                    reward = int(np.round(np.random.normal(mus[response],
                                                           self.reward_sd)))
                    prompt += f"{letter}[/HUMAN_RESPONSE]. You receive {reward} points."
                    rows.append({
                        "participant_id": participant, "task_id": game, "trial": trial,
                        "mu1": mu1, "mu2": mu2, "choice": response + 1,
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

    task = DualStochasticBandit()
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