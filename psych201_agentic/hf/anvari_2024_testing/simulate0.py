# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/anvari_2024_testing``
(multi-armed bandit), format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import random

import numpy as np
import pandas as pd
from tqdm import tqdm

PAPER = "Hugging-Brain/anvari_2024_testing"

INSTRUCTIONS = (
    "You play a game with five buttons. On each trial you click one button and it "
    "reveals a number of points; your goal is to earn as many points as possible. "
    "The screen shows the trial number, how many times each button has been selected, "
    "the average points per click for each button, and your total points so far. For "
    "every 100 points you earn a bonus of 1p. On each trial press the letter for the "
    "button you choose: {buttons}.")


def _shuffled_letters(pid, letters):
    rnd = random.Random(f"{PAPER}:{pid}")
    ls = list(letters)
    rnd.shuffle(ls)
    return ls


def _fmt(x):
    return f"{x:g}" if isinstance(x, (int, float)) else str(x)


class FiveArmedBandit:
    """Multi-armed bandit, exp0 of Anvari et al. (2024), "Testing the convergent
    validity, domain generality, and temporal stability of selected measures of
    people's tendency to explore", Nature Communications 15, 7721.

    Design (Methods, "Multi-armed bandit", p. 14): five buttons each with a
    non-negative payout; 1 practice block of 20 trials plus 4 incentivized
    blocks of 40 trials; each block has fresh buttons. Response tokens
    (Button 1..5 = A..E) are shuffled per participant exactly as in the repo's
    build_jsonl.py.

    ASSUMPTION: the payoff distributions come from the shipped data, not the
    paper (they are in its Supplemental Information): each button's mean
    (player_weight0..4) is an integer drawn uniformly from 43..60 per block, and
    a click pays max(0, round(Normal(mean, 5))) points (player_payoff_1).
    """

    def __init__(self):
        self.name = "anvari_2024_testing_exp0"
        self.n_blocks = 5          # task_id 0 = practice, 1..4 = incentivized
        self.practice_trials = 20
        self.incentivized_trials = 40
        self.mean_range = (43, 60)
        self.sd = 5.0

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            pid = f"P{participant:03d}"
            letters = _shuffled_letters(pid, ["A", "B", "C", "D", "E"])
            btn_to_letter = {i: letters[i] for i in range(5)}
            buttons = ", ".join(f"Button {i + 1} = {btn_to_letter[i]}"
                                for i in range(5))
            prompt = INSTRUCTIONS.format(buttons=buttons)
            for task_id in range(self.n_blocks):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                n = (self.practice_trials if task_id == 0
                     else self.incentivized_trials)
                tag = "practice" if task_id == 0 else "incentivized"
                means = np.random.randint(self.mean_range[0], self.mean_range[1] + 1, size=5)
                prompt += f"\n{tag} block begins with five new buttons."
                for trial in range(n):
                    prompt += (f"\n{tag} trial: you press [HUMAN_RESPONSE]")
                    letter = agent(prompt, choice_options=letters)
                    response = letters.index(letter)
                    pay = int(max(0, round(np.random.normal(means[response], self.sd))))
                    prompt += f"{letter}[/HUMAN_RESPONSE]; it pays {_fmt(pay)} points."
                    rows.append({
                        "participant_id": pid, "session": "time1",
                        "task_id": task_id, "trial": trial, "response": response,
                        "phase": "practice" if task_id == 0 else "test",
                        "player_payoff_1": pay,
                        **{f"player_weight{i}": int(means[i]) for i in range(5)},
                    })
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "session", "task_id", "trial", "response", "phase",
            "player_payoff_1", "player_weight0", "player_weight1", "player_weight2",
            "player_weight3", "player_weight4",
        ])
        return df, prompts


class _RandomAgent:
    def __init__(self):
        self.rng = np.random.default_rng()

    def __call__(self, prompt, choice_options):
        return str(self.rng.choice(list(choice_options)))


def main():
    parser = argparse.ArgumentParser(
        description="Smoke-test this simulator with a uniform-random agent.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3)
    parser.add_argument("--max-chars", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)
        random.seed(args.seed)

    task = FiveArmedBandit()
    df, prompts = task.simulate(_RandomAgent(), args.num_simulations,
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
    print(prompts[0][:400])
    print("...")
    print("first prompt, tail:")
    print(prompts[0][-200:])


if __name__ == "__main__":
    main()
