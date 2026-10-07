# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/pirrone_2024_subjective``,
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
    "You are choosing between pairs of lotteries. On each trial two lotteries are "
    "shown side by side; each lottery has two equally likely outcomes. Pick the "
    "lottery that seems to you like the better gamble overall. "
    "Press {left_letter} to choose the left lottery or {right_letter} to choose the "
    "right lottery."
)


class Experiment:
    """Risky-choice experiment (one session of 450 two-outcome-lottery choices),
    Pirrone (2024), "Subjective utility modulates the effect of overall stimulus
    intensity on decision-making" (unpublished; OSF project xvnjd, no manuscript
    PDF). Design reconstructed from the shipped data + OSF README.

    On each trial two two-outcome lotteries appear side by side: the left pays
    o1 or o2, the right pays o3 or o4 (each outcome equally likely, values 1..100).
    The participant presses a letter key to choose the lottery they judge the
    better gamble. The left lottery's sum and the right lottery's sum are
    related to the trial's magnitude and magnitude_difference
    (left_sum + right_sum = magnitude, left_sum - right_sum =
    magnitude_difference); magnitude is drawn around 200, magnitude_difference
    is 0 on ~60% of trials and otherwise uniform over +/-1..+/-50, and each
    lottery's two outcomes split its sum uniformly over the feasible [1,100]
    range. The higher-expected-outcome lottery is the accuracy target
    (max_ev_lottery).

    Letter mapping: per-participant, as in build_jsonl.py — even-ranked
    participant ids map A -> left / B -> right, odd-ranked ids B -> left /
    A -> right.

    Coding (from the source data): response 1 = the LEFT lottery (o1/o2),
    0 = the RIGHT lottery (o3/o4); max_ev_lottery = (o1+o2 > o3+o4), i.e. 1 =
    the LEFT lottery has the larger outcome sum; prefer_variance = 1 iff the
    chosen lottery has the larger outcome spread (response == variance_left).
    The source's accuracy_unequal equals mean(response == max_ev_lottery) on
    unequal trials, which pins this mapping. The simulator follows it
    (round-trip reproducible).

    ASSUMPTION: stimulus generation (magnitude, magnitude_difference, sum-split)
    is a data-driven reconstruction; the paper has no methods section.

    rt (reaction time) and nonlinear_preference (per-participant fitted latent)
    are dropped as not producible by a text simulator; every other exp0.csv
    column is reproduced.
    """

    def __init__(self):
        self.name = "pirrone_2024_subjective_exp0"
        self.num_trials = 450

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        rng = np.random.default_rng()
        for participant in tqdm(range(num_simulations)):
            # per-participant letter mapping, exactly as in build_jsonl.py
            left_letter, right_letter = ("A", "B") if participant % 2 == 0 else ("B", "A")
            prompt = INSTRUCTIONS.format(left_letter=left_letter,
                                         right_letter=right_letter)
            for trial in range(self.num_trials):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                # --- generative stimulus process ---
                while True:
                    magnitude = int(np.round(rng.normal(201.0, 62.0)))
                    if rng.random() < 0.603:
                        magnitude_difference = 0
                    else:
                        magnitude_difference = int(rng.integers(-50, 51))
                    if (magnitude - magnitude_difference) % 2:
                        magnitude += 1
                    left_sum = (magnitude + magnitude_difference) // 2
                    right_sum = (magnitude - magnitude_difference) // 2
                    if (2 <= left_sum <= 200 and 2 <= right_sum <= 200
                            and 14 <= magnitude <= 392):
                        break
                o1 = int(rng.integers(max(1, left_sum - 100),
                                      min(100, left_sum - 1) + 1))
                o2 = left_sum - o1
                o3 = int(rng.integers(max(1, right_sum - 100),
                                      min(100, right_sum - 1) + 1))
                o4 = right_sum - o3
                # --- free choice ---
                prompt += ("\nYou see two lotteries. The left pays either "
                           f"{o1} or {o2}; the right pays either {o3} or {o4}. "
                           "You press [HUMAN_RESPONSE]")
                letter = agent(prompt, choice_options=[left_letter, right_letter])
                response = 1 if letter == left_letter else 0
                prompt += f"{letter}[/HUMAN_RESPONSE]."
                # --- derived columns ---
                left_range = abs(o1 - o2)
                right_range = abs(o3 - o4)
                max_ev_lottery = 1 if (o1 + o2) > (o3 + o4) else 0
                variance_left = 1 if left_range > right_range else 0
                variance_difference = abs(left_range - right_range)
                chose_higher_variance = (variance_left == 1 and response == 1) or \
                                        (variance_left == 0 and response == 0)
                prefer_variance = int(chose_higher_variance)
                rows.append({
                    "participant_id": participant, "trial": trial,
                    "response": response, "o1": o1, "o2": o2, "o3": o3, "o4": o4,
                    "magnitude_difference": magnitude_difference,
                    "magnitude": magnitude, "variance_left": variance_left,
                    "max_ev_lottery": max_ev_lottery,
                    "variance_difference": variance_difference,
                    "prefer_variance": prefer_variance,
                })
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "o1", "o2", "o3", "o4",
            "magnitude_difference", "magnitude", "variance_left",
            "max_ev_lottery", "variance_difference", "prefer_variance",
        ])
        # accuracy_unequal: per-participant share of responses matching
        # max_ev_lottery on unequal-magnitude trials (as in the shipped data).
        if len(df):
            acc = df[df["magnitude_difference"] != 0].groupby("participant_id").apply(
                lambda s: (s["response"] == s["max_ev_lottery"]).mean())
            df["accuracy_unequal"] = df["participant_id"].map(acc)
        else:
            df["accuracy_unequal"] = np.nan
        df = df[[
            "participant_id", "trial", "response", "o1", "o2", "o3", "o4",
            "magnitude_difference", "magnitude", "variance_left",
            "max_ev_lottery", "accuracy_unequal", "variance_difference",
            "prefer_variance",
        ]]
        return df, prompts


def _random_agent(prompt, choice_options):
    return str(np.random.choice(choice_options))


def main():
    parser = argparse.ArgumentParser(
        description="Smoke-test this simulator with a uniform-random agent.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3,
                        help="number of simulated participants (default: 3)")
    parser.add_argument("--max-chars", type=int, default=None,
                        help="stop each participant at the block boundary at/past this many chars")
    parser.add_argument("--seed", type=int, default=None,
                        help="numpy random seed, for reproducible runs")
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    task = Experiment()
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