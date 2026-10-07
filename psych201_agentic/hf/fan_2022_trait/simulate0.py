# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/fan_2022_trait`` (Study 1 bandit),
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp0).
INSTRUCTIONS = (
    "You are playing a two-slot-machine game to earn as many coins as you can. "
    "In each round, a fresh pair of slot machines appears on screen, one on the left and one on the right. "
    "On each play, you choose one machine; the machine pays out a number of coins, which may be positive or negative. "
    "Each round lasts 10 plays, and then a new pair of machines appears. "
    "Press A to play the left machine or B to play the right machine."
)

CONDITIONS = {
    1: (True, False),   # FS: left fluctuates, right stable
    2: (False, True),   # SF: left stable, right fluctuates
    3: (True, True),    # FF: both fluctuate
    4: (False, False),  # SS: both stable
}


def _fmt(x):
    f = float(x)
    return str(int(f)) if f == int(f) else str(f)


class TwoSlotBandit:
    """Restless two-slot-machine bandit, Study 1 of Fan, Gershman & Phelps
    (2023), "Trait somatic anxiety is associated with reduced directed
    exploration and underestimation of uncertainty", Nature Human Behaviour,
    7, 102-113.

    Design (Supplementary Methods, "Behavioral Task / Experiment 1", paper
    SI p.2-3): 30 rounds of 10 free A/B choices; each round draws a fresh pair
    of slot machines, one stable (mean fixed across the round) and one
    fluctuating (mean drifts across plays); rewards can be positive or
    negative; choice 1 = left machine (option 1, press A), choice 0 = right
    machine (option 2, press B), as in the source data (C = 1 pays reward1).

    ASSUMPTION: the paper's Methods and original task code are paywalled /
    absent from OSF, so the generative constants were reverse-engineered from
    the shipped exp0.csv (documented in the dataset README's Online experiment
    note) and re-verified here: per-round initial means mu ~ round(N(0, 10));
    fluctuating-arm drift per play ~ round(N(0, 2)); reward ~ round(N(mu, 1));
    condition 1=FS / 2=SF / 3=FF / 4=SS per round (F=fluctuating, S=stable).

    ASSUMPTION: condition is drawn uniformly per round (the real sequences are
    independently randomized per participant and balanced ~25% each).

    The DataFrame matches exp0.csv minus ``rt``, the model-derived columns
    (V, RU, VTU, TU, *_old, est_m1/2, est_s1/2, C_pred, C_pred_prob) and the
    questionnaire/demographic columns (age, gender, STAIT_*, STICSAT_*,
    Factor*).
    """

    def __init__(self):
        self.name = "fan_2022_trait_exp0"
        self.num_rounds = 30     # fresh pair of slot machines each round
        self.num_plays = 10      # free choices per round
        self.init_sd = 10.0      # mu ~ round(N(0, init_sd)) per arm per round
        self.drift_sd = 2.0      # fluctuating arm's mean drift ~ round(N(0, drift_sd))
        self.reward_sd = 1.0     # reward ~ round(N(mu, reward_sd))

    def _new_mean(self):
        return int(np.round(np.random.normal(0.0, self.init_sd)))

    def _step(self):
        return int(np.round(np.random.normal(0.0, self.drift_sd)))

    def _reward(self, mu):
        return int(np.round(np.random.normal(mu, self.reward_sd)))

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            prompt = INSTRUCTIONS
            for rnd in range(self.num_rounds):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                condition = int(np.random.randint(1, 5))
                fluc1, fluc2 = CONDITIONS[condition]
                mu1, mu2 = self._new_mean(), self._new_mean()
                prompt += f"\nRound {rnd + 1}: A fresh pair of slot machines appears."
                for trial in range(self.num_plays):
                    prompt += "\nYou press [HUMAN_RESPONSE]"
                    letter = agent(prompt, choice_options=["A", "B"])
                    response = 1 if letter == "A" else 0
                    side = "left" if response == 1 else "right"
                    reward1 = self._reward(mu1)
                    reward2 = self._reward(mu2)
                    reward = reward1 if response == 1 else reward2
                    if reward >= 0:
                        prompt += (f"{letter}[/HUMAN_RESPONSE] for the {side} machine. "
                                   f"You gain {_fmt(reward)} coins.")
                    else:
                        prompt += (f"{letter}[/HUMAN_RESPONSE] for the {side} machine. "
                                   f"You lose {_fmt(-reward)} coins.")
                    chosen = mu1 if response == 1 else mu2
                    other = mu2 if response == 1 else mu1
                    rows.append({
                        "participant_id": f"P{participant:03d}",
                        "task_id": rnd, "trial": trial, "response": response,
                        "reward": reward, "correct": int(chosen > other),
                        "condition": condition, "mu1": mu1, "mu2": mu2,
                        "reward1": reward1, "reward2": reward2,
                    })
                    if fluc1:
                        mu1 += self._step()
                    if fluc2:
                        mu2 += self._step()
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "task_id", "trial", "response", "reward",
            "correct", "condition", "mu1", "mu2", "reward1", "reward2",
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

    task = TwoSlotBandit()
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
