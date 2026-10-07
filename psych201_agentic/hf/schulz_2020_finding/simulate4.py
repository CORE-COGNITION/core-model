# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp4 of ``Hugging-Brain/schulz_2020_finding``,
format-identical to the repo's ``transcripts4.jsonl``.

``uv run simulate4.py -n 3`` smoke-tests with a uniform-random agent; or import
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


def _changepoint_fn(rng, peak_idx):
    """8-arm change-point function peaking at 0-indexed ``peak_idx`` (1..6). Rises
    linearly from arm 0 (fmin~U[2,10]) to the peak (fmax~U[40,48]) and falls
    linearly to arm 7 (fmin), as in Experiment 5 (Fig. 15)."""
    fmin = rng.uniform(2.0, 10.0)
    fmax = rng.uniform(40.0, 48.0)
    fn = []
    for i in range(8):
        if i <= peak_idx:
            fn.append(fmin + (fmax - fmin) * (i / peak_idx))
        else:
            fn.append(fmax - (fmax - fmin) * ((i - peak_idx) / (7 - peak_idx)))
    return fn


class ChangepointBandit:
    """Experiment 5 of Schulz, Franklin & Gershman (2020), "Finding structure in
    multi-armed bandits", Cognitive Psychology, 119, 101261 (bioRxiv 432534).

    Design (Experiment 5, Design/Procedure, pp. 30-31): two between-subjects
    groups, ``structure`` (latent functions sampled from a change-point kernel,
    rising linearly to a peak then falling) and ``random`` (a matched scrambled
    set where every arm's reward but the best one's is shuffled). Within the
    structure condition, 5 rounds peak on each of the middle six arms (arms 2-7).
    Group is assigned at random per participant; the stored file's condition
    column records it (structure N=87, random N=72 by raw participant id).

    ASSUMPTION: paper states eps ~ N(0, 0.1); the shipped data show ~0.3 sd
    (median 0.28), so eps ~ N(0, 0.3) is used per the data-authoritative rule.
    Latent peak values are drawn fresh per round (the exact 90-function pool is
    not shipped).

    The DataFrame matches exp4.csv minus ``rt``.
    """

    def __init__(self):
        self.name = "schulz_2020_finding_exp4"
        self.num_rounds = 30
        self.num_trials = 10
        self.num_arms = 8
        self.noise_sd = 0.3

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            prompt = INSTRUCTIONS + "\n"
            rng = np.random.default_rng(participant)
            condition = "structure" if rng.random() < 0.5 else "random"
            peaks = [p for p in range(1, 7) for _ in range(5)]   # 5 rounds per peak arm
            rng.shuffle(peaks)
            for round_idx in range(self.num_rounds):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                peak = peaks[round_idx]
                fn = _changepoint_fn(rng, peak)
                if condition == "random":
                    best = fn[peak]
                    mid = [v for i, v in enumerate(fn) if i != peak]
                    rng.shuffle(mid)
                    vals = iter(mid)
                    fn = [next(vals) if i != peak else best for i in range(8)]
                prompt += f"\nRound {round_idx + 1} of 30.\n"
                for trial in range(self.num_trials):
                    prompt += f"Trial {trial + 1}: You press [HUMAN_RESPONSE]"
                    key = agent(prompt, choice_options=KEYS)
                    response = KEYS.index(key)
                    reward = float(np.random.normal(fn[response], self.noise_sd))
                    prompt += f"{key}[/HUMAN_RESPONSE] and gain {round(reward, 2)} points.\n"
                    rows.append({
                        "participant_id": participant + 1, "task_id": round_idx,
                        "trial": trial, "response": response, "condition": condition,
                        "round": round_idx + 1, "arm": response + 1, "reward": reward,
                    })
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "task_id", "trial", "response", "condition",
            "round", "arm", "reward",
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

    task = ChangepointBandit()
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