# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/dezfouli_2019_models``,
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
    "You see two buttons side by side: a left button and a right button. Your task is to "
    "press one button on each trial to try to earn food rewards. On a trial, press the "
    "left button by typing L, or the right button by typing R. Pressing a button "
    "sometimes earns you a food reward (an M&M chocolate or a BBQ-flavoured cracker) and "
    "sometimes earns you nothing. The chance of earning a reward from each button changes "
    "from time to time, so pay attention to what happens and try to earn as many rewards "
    "as you can."
)


class TwoArmedBandit:
    """Two-armed bandit, Experiment 1 (main task) of Dezfouli et al. (2019),
    "Models that learn how humans learn", PLoS Comput Biol 15(6): e1006903.

    Design (Methods, "Task", p. 2): 12 blocks, each lasting 40 seconds and
    separated by a 12-second inter-block interval. Within each block one action
    (left or right) is better than the other in reward probability; the better
    action's reward probability is 0.25, 0.125 or 0.08, and the other action's
    reward probability is always 0.05. There are thus six (better-prob, better
    side) pairs, each repeated twice across the 12 blocks (probabilities fixed
    within a block). Every trial is a free choice: press L (left, response 0)
    or R (right, response 1), then observe the binary reward.

    ASSUMPTION: blocks are time-limited (40 s) self-paced, so the real data
    hold a variable number of trials per participant per block
    (mean ~109, sd ~34, min 6, max 202). A text simulator has no reaction-time
    process, so each block's trial count is drawn from
    round(N(mean=109, sd=34)) clipped to [6, inf), matching the observed spread.
    exp0.csv has no RT column, so none is produced here.

    ASSUMPTION: the block schedule (which better_prob and which side for each
    of the 12 blocks) is not recorded in exp0.csv, so the six
    (better_prob, better_side) pairs are shuffled and each repeated twice per
    participant, matching the paper's "six pairs repeated twice" rule. The
    per-block observed reward rates on the better action (approx 0.12-0.17)
    sit between the paper's 0.08-0.25 values because of the shuffle + sparse
    on-the-better-action choices; the worse-action reward rate matches the
    paper's 0.05 almost exactly.

    The DataFrame mirrors exp0.csv minus the anonymization of participant_id
    (here the integer simulation index is used).
    """

    def __init__(self):
        self.name = "dezfouli_2019_models_exp0"
        self.num_blocks = 12
        self.worse_prob = 0.05
        self.better_probs = [0.25, 0.125, 0.08]   # better-action reward probability levels
        self.trials_mean = 109.0                  # mean trials per participant-block (40 s)
        self.trials_sd = 34.0                     # std of trials per participant-block

    def _block_schedule(self, rng):
        pairs = [(p, side) for p in self.better_probs for side in (0, 1)]
        schedule = list(pairs) + list(pairs)      # six pairs repeated twice = 12 blocks
        rng.shuffle(schedule)
        return schedule

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        conditions = ["healthy", "depression", "bipolar"]
        for participant in tqdm(range(num_simulations)):
            rng = np.random.default_rng()         # not seeded: fresh random stream
            condition = str(rng.choice(conditions))
            prompt = INSTRUCTIONS
            schedule = self._block_schedule(rng)
            trial = 0
            for block, (better_prob, better_side) in enumerate(schedule):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                n_trials = int(max(6, round(rng.normal(self.trials_mean, self.trials_sd))))
                for _ in range(n_trials):
                    prompt += "\nYou press [HUMAN_RESPONSE]"
                    letter = agent(prompt, choice_options=["L", "R"])
                    response = 0 if letter == "L" else 1
                    p = better_prob if response == better_side else self.worse_prob
                    reward = int(rng.random() < p)
                    outcome = "You earn a food reward." if reward == 1 else "You receive nothing."
                    prompt += f"{letter}[/HUMAN_RESPONSE]. {outcome}"
                    best_action = 1 if response == better_side else 0
                    rows.append({
                        "participant_id": participant, "trial": trial,
                        "response": response, "block": block, "reward": reward,
                        "condition": condition, "best_action": best_action,
                    })
                    trial += 1
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "block", "reward",
            "condition", "best_action",
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