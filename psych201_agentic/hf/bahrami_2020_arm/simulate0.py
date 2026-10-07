# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/bahrami_2020_arm``, format-identical
to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp0).
INSTRUCTIONS = (
    "Welcome to the 4-Arm Bandit experiment.\n"
    "On each trial you will see four slot machines, labeled A, B, C, and D. "
    "Choose exactly one machine by pressing the corresponding key. "
    "After your choice you will see the reward you obtained from that machine. "
    "You will not see the rewards the other machines would have paid. "
    "Each machine's payoff drifts slowly over time, so keep trying different "
    "machines to find out which is paying well, while mostly choosing the ones "
    "that have been good recently. You have 4 seconds to respond; if you do not "
    "respond in time the trial is skipped and you earn no reward. "
    "The task lasts 150 trials. Press one of A, B, C, or D to choose a machine."
)

ARMS = ["A", "B", "C", "D"]  # fixed 1:1 with response 0..3 (build_jsonl.py policy)

# The three payoff schedules of exp0.csv, PAYOFFS[version][trial] = [reward_c1..reward_c4]
# (150 trials each; every participant of a version saw exactly this schedule).
PAYOFFS = {
    0: [
        [84, 87, 42, 23], [90, 90, 46, 18], [80, 84, 53, 28], [87, 81, 50, 24], [86, 92, 61, 28], [75, 78, 55, 30],
        [71, 78, 50, 34], [75, 83, 58, 43], [77, 80, 52, 30], [70, 80, 43, 28], [65, 91, 49, 29], [77, 90, 53, 30],
        [66, 79, 44, 29], [66, 90, 45, 30], [67, 81, 45, 35], [59, 75, 39, 32], [67, 82, 54, 33], [64, 82, 51, 20],
        [61, 87, 42, 28], [62, 85, 50, 27], [55, 87, 46, 32], [59, 87, 51, 34], [56, 79, 50, 38], [57, 75, 45, 34],
        [61, 75, 47, 34], [59, 74, 40, 33], [50, 82, 42, 37], [57, 72, 48, 41], [60, 73, 48, 37], [66, 71, 47, 38],
        [65, 57, 48, 34], [64, 62, 48, 28], [63, 56, 51, 23], [61, 58, 49, 37], [57, 61, 54, 30], [56, 67, 57, 30],
        [59, 64, 52, 29], [48, 65, 56, 27], [46, 64, 46, 27], [59, 60, 42, 35], [55, 63, 47, 26], [55, 63, 48, 14],
        [56, 58, 50, 17], [53, 56, 52, 20], [52, 55, 60, 17], [56, 61, 59, 16], [52, 55, 49, 17], [58, 51, 54, 18],
        [59, 57, 56, 23], [65, 52, 51, 14], [67, 52, 52, 18], [67, 52, 51, 26], [71, 66, 48, 17], [71, 57, 48, 19],
        [69, 57, 55, 14], [69, 46, 48, 12], [68, 68, 47, 8], [61, 60, 51, 19], [63, 57, 63, 19], [58, 54, 51, 23],
        [62, 53, 61, 18], [53, 50, 53, 18], [59, 61, 50, 13], [65, 50, 54, 26], [61, 58, 52, 35], [65, 54, 54, 27],
        [61, 56, 61, 23], [63, 66, 61, 28], [55, 71, 62, 21], [61, 57, 64, 33], [54, 56, 58, 29], [50, 51, 58, 24],
        [49, 50, 53, 34], [47, 61, 50, 30], [49, 63, 51, 31], [49, 68, 57, 40], [42, 56, 44, 41], [48, 59, 43, 39],
        [42, 66, 48, 35], [42, 56, 50, 40], [43, 56, 51, 35], [48, 59, 49, 37], [39, 59, 48, 31], [32, 55, 54, 36],
        [38, 52, 51, 40], [43, 61, 58, 34], [43, 60, 51, 32], [40, 58, 62, 32], [45, 61, 64, 43], [50, 56, 60, 34],
        [39, 54, 62, 39], [47, 53, 64, 38], [35, 53, 50, 38], [40, 57, 60, 40], [40, 54, 50, 36], [36, 49, 65, 39],
        [33, 56, 68, 40], [37, 55, 71, 48], [36, 51, 78, 45], [27, 54, 79, 47], [35, 59, 79, 46], [28, 63, 85, 43],
        [38, 62, 80, 34], [36, 62, 82, 43], [31, 54, 83, 50], [35, 58, 85, 38], [35, 55, 71, 41], [34, 52, 74, 42],
        [23, 59, 83, 46], [34, 57, 69, 53], [33, 51, 75, 52], [18, 49, 64, 46], [33, 47, 68, 51], [34, 55, 74, 43],
        [31, 46, 80, 38], [30, 40, 70, 40], [36, 44, 73, 45], [26, 47, 66, 39], [30, 46, 71, 49], [24, 50, 70, 37],
        [33, 47, 71, 35], [29, 45, 65, 39], [29, 43, 71, 45], [37, 32, 73, 51], [37, 48, 65, 48], [33, 35, 73, 46],
        [37, 35, 66, 41], [45, 41, 59, 37], [29, 37, 69, 40], [34, 40, 75, 47], [32, 40, 67, 40], [43, 40, 63, 42],
        [48, 44, 74, 37], [35, 45, 70, 49], [39, 37, 77, 47], [42, 35, 70, 46], [34, 34, 78, 56], [29, 39, 74, 54],
        [33, 28, 70, 46], [33, 31, 68, 54], [33, 33, 67, 60], [37, 26, 63, 56], [33, 34, 65, 57], [36, 35, 60, 51],
        [44, 38, 60, 55], [47, 35, 62, 48], [46, 47, 61, 57], [46, 35, 70, 43], [46, 44, 60, 59], [39, 35, 56, 51],
    ],
    1: [
        [20, 33, 73, 19], [15, 28, 76, 9], [16, 37, 81, 16], [10, 30, 78, 17], [16, 38, 78, 21], [15, 37, 76, 18],
        [17, 37, 69, 9], [18, 36, 74, 18], [8, 48, 71, 4], [14, 39, 85, 3], [17, 45, 65, 1], [13, 48, 81, 6],
        [10, 44, 72, 16], [25, 46, 70, 9], [23, 43, 66, 7], [12, 60, 70, 5], [15, 51, 65, 7], [13, 49, 69, 16],
        [20, 48, 78, 5], [16, 61, 66, 13], [14, 60, 66, 11], [17, 58, 64, 8], [20, 52, 70, 8], [21, 57, 73, 23],
        [20, 54, 75, 19], [23, 52, 60, 19], [23, 55, 73, 21], [16, 58, 72, 16], [15, 51, 69, 21], [10, 46, 62, 22],
        [10, 34, 70, 19], [11, 51, 56, 20], [13, 49, 65, 18], [14, 52, 58, 25], [27, 46, 58, 18], [14, 58, 62, 19],
        [20, 48, 55, 18], [13, 52, 61, 25], [26, 48, 56, 17], [19, 45, 53, 23], [26, 57, 61, 22], [25, 46, 54, 27],
        [31, 49, 65, 18], [30, 39, 50, 30], [25, 39, 62, 21], [37, 33, 61, 26], [30, 33, 59, 22], [38, 37, 62, 17],
        [35, 41, 50, 16], [36, 37, 49, 13], [37, 38, 46, 2], [37, 29, 48, 10], [35, 30, 56, 15], [32, 29, 59, 6],
        [39, 38, 48, 12], [34, 45, 47, 18], [40, 34, 50, 15], [49, 41, 50, 21], [45, 45, 49, 23], [48, 45, 46, 18],
        [49, 48, 45, 16], [52, 46, 53, 22], [48, 44, 48, 13], [48, 51, 42, 13], [55, 52, 38, 17], [49, 55, 41, 18],
        [39, 57, 43, 19], [43, 49, 39, 24], [52, 54, 46, 32], [44, 55, 41, 33], [52, 49, 43, 24], [48, 55, 50, 27],
        [52, 53, 45, 12], [55, 59, 43, 25], [59, 56, 40, 28], [54, 51, 33, 24], [38, 54, 39, 29], [42, 54, 39, 31],
        [39, 60, 35, 31], [37, 59, 30, 37], [41, 56, 32, 30], [56, 52, 26, 25], [43, 53, 22, 19], [52, 71, 17, 29],
        [49, 69, 26, 31], [60, 69, 32, 30], [59, 68, 34, 22], [64, 61, 34, 31], [50, 76, 35, 37], [68, 62, 35, 20],
        [59, 67, 38, 25], [57, 63, 33, 17], [57, 69, 41, 19], [62, 69, 27, 16], [64, 78, 30, 25], [57, 82, 30, 14],
        [58, 81, 38, 23], [65, 73, 35, 32], [54, 73, 36, 34], [49, 83, 40, 35], [58, 76, 40, 26], [51, 75, 46, 39],
        [61, 83, 49, 39], [62, 85, 47, 40], [71, 89, 47, 42], [73, 94, 47, 38], [68, 90, 38, 33], [65, 87, 37, 30],
        [66, 97, 30, 32], [76, 98, 30, 36], [80, 95, 38, 43], [72, 96, 29, 23], [76, 95, 26, 36], [74, 91, 30, 35],
        [75, 91, 30, 28], [75, 94, 39, 32], [70, 94, 34, 36], [71, 89, 34, 42], [76, 92, 32, 31], [72, 93, 42, 34],
        [72, 80, 50, 30], [72, 84, 40, 28], [76, 81, 27, 29], [74, 79, 39, 33], [80, 80, 33, 27], [71, 76, 39, 39],
        [73, 73, 35, 42], [76, 77, 32, 36], [78, 67, 30, 34], [73, 65, 31, 25], [81, 58, 33, 38], [81, 66, 29, 36],
        [72, 58, 31, 34], [68, 66, 27, 35], [71, 56, 27, 37], [62, 64, 33, 32], [71, 62, 36, 30], [76, 58, 26, 27],
        [63, 54, 22, 16], [66, 50, 30, 19], [78, 55, 26, 15], [73, 45, 36, 20], [68, 48, 34, 23], [55, 58, 33, 16],
        [65, 65, 28, 28], [59, 57, 30, 28], [64, 56, 38, 31], [55, 47, 27, 34], [51, 41, 36, 37], [52, 48, 35, 43],
    ],
    2: [
        [42, 69, 20, 28], [42, 81, 31, 21], [41, 74, 25, 16], [40, 76, 16, 9], [40, 72, 26, 8], [39, 80, 17, 21],
        [34, 76, 20, 12], [36, 81, 21, 28], [36, 71, 17, 19], [29, 74, 15, 14], [37, 71, 14, 31], [33, 83, 17, 26],
        [24, 82, 7, 16], [39, 75, 5, 28], [34, 75, 7, 38], [31, 73, 15, 34], [33, 70, 19, 33], [32, 68, 10, 42],
        [35, 70, 8, 36], [42, 68, 12, 39], [36, 72, 1, 37], [31, 72, 1, 34], [27, 63, 2, 38], [22, 69, 1, 42],
        [24, 62, 4, 33], [34, 69, 6, 41], [22, 70, 6, 44], [37, 68, 8, 35], [33, 71, 9, 39], [35, 76, 5, 37],
        [38, 71, 8, 32], [35, 76, 13, 31], [44, 67, 18, 36], [42, 71, 22, 34], [32, 67, 17, 34], [27, 67, 15, 29],
        [22, 72, 25, 32], [31, 70, 19, 39], [39, 64, 24, 26], [29, 66, 24, 19], [32, 65, 20, 13], [32, 64, 24, 21],
        [32, 70, 16, 29], [26, 52, 20, 37], [33, 66, 23, 27], [29, 56, 25, 30], [30, 59, 16, 31], [28, 57, 14, 29],
        [30, 56, 21, 28], [26, 57, 21, 35], [20, 59, 20, 43], [29, 57, 15, 36], [21, 52, 21, 40], [31, 57, 19, 35],
        [31, 51, 23, 44], [34, 55, 17, 34], [37, 65, 28, 25], [40, 56, 23, 32], [35, 52, 14, 40], [39, 53, 21, 31],
        [29, 54, 15, 36], [39, 53, 18, 35], [34, 57, 24, 30], [41, 55, 23, 30], [37, 50, 21, 42], [32, 46, 35, 34],
        [29, 43, 29, 33], [38, 46, 40, 35], [31, 49, 39, 29], [38, 40, 29, 26], [39, 37, 30, 30], [28, 38, 29, 34],
        [37, 34, 36, 32], [29, 49, 28, 28], [36, 39, 32, 31], [41, 37, 49, 33], [34, 37, 40, 40], [36, 32, 39, 46],
        [31, 48, 41, 37], [33, 28, 49, 43], [37, 35, 44, 45], [35, 33, 39, 46], [33, 44, 35, 47], [34, 36, 37, 42],
        [44, 42, 45, 39], [37, 45, 43, 42], [38, 44, 43, 45], [41, 41, 38, 46], [36, 38, 51, 48], [34, 44, 51, 52],
        [40, 48, 47, 56], [41, 38, 47, 49], [31, 38, 50, 52], [22, 48, 57, 56], [29, 44, 55, 41], [29, 41, 63, 54],
        [31, 44, 60, 53], [27, 42, 58, 49], [34, 41, 59, 64], [31, 44, 59, 55], [27, 43, 62, 53], [33, 46, 59, 48],
        [32, 37, 68, 47], [30, 41, 70, 54], [31, 36, 59, 55], [28, 41, 58, 50], [26, 47, 53, 46], [35, 48, 57, 57],
        [43, 50, 58, 38], [33, 38, 54, 39], [32, 43, 63, 39], [27, 42, 52, 35], [36, 47, 57, 47], [31, 46, 65, 38],
        [31, 50, 59, 46], [36, 45, 64, 42], [33, 43, 65, 40], [31, 49, 72, 39], [42, 55, 66, 31], [44, 55, 68, 38],
        [33, 56, 76, 29], [43, 48, 72, 26], [22, 60, 79, 27], [32, 64, 84, 29], [28, 66, 77, 29], [28, 55, 81, 27],
        [25, 63, 83, 27], [42, 58, 84, 31], [37, 57, 79, 32], [32, 53, 83, 23], [32, 52, 83, 37], [27, 51, 76, 32],
        [38, 45, 76, 30], [40, 40, 80, 32], [27, 40, 71, 26], [39, 53, 80, 34], [41, 32, 78, 31], [41, 35, 87, 31],
        [31, 35, 91, 31], [35, 28, 81, 26], [40, 32, 88, 14], [50, 31, 83, 23], [43, 33, 79, 20], [40, 32, 90, 21],
        [40, 29, 92, 12], [38, 30, 82, 16], [33, 37, 82, 13], [34, 30, 75, 10], [42, 49, 79, 10], [49, 37, 78, 15],
    ],
}
VERSIONS = [0, 1, 2]


class FourArmBandit:
    """Online restless 4-arm bandit (Daw et al. 2006 paradigm), the single
    experiment of the Bahrami, Navajas, Hertz, Wang & Wang (2020) 4-Arm Bandit
    dataset (OSF https://osf.io/f3t2a/; data description 4ArmBanditDescription.pdf).

    Design: 150 trials. Each of four arms has a drifting true payoff reward_c
    (integer). The participant chooses one arm and receives exactly that arm's
    current true payoff as reward; the other arms' payoffs are unseen. A trial is
    missed (no response, no reward) when the participant fails to respond within
    4 s. The drift schedule is a between-subject factor (version 0/1/2).

    Payoffs: the study used three fixed payoff schedules, one per version; in
    exp0.csv reward_c1..reward_c4 are identical on every trial for all participants
    of a version (329/312/324 participants, no missing values, also on missed
    trials) and the received reward equals the chosen arm's payoff on all 139816
    answered trials. The simulator replays these schedules (PAYOFFS) instead of
    drawing a new random walk, so a simulated participant faces the same bandit as
    the human participants (until 2026-09-21 it drew a fresh integer Gaussian walk,
    step SD 6 clipped to [1, 98], from the version's first-trial payoffs; its
    best-arm gaps and crossings differed from the ones participants saw).

    The PDF does not give the remaining constants; they are recovered from the
    shipped exp0.csv (data-authoritative):

    ASSUMPTION (version): version is assigned uniformly at random per
    participant from {0,1,2} (empirically ~329/312/324 of 965).

    ASSUMPTION (miss rate): a trial is missed with probability ~0.034
    (empirically 4934/144750 trials), independent of the trial/choice.

    The DataFrame matches exp0.csv minus ``rt`` (a text simulator cannot produce
    reaction times). Columns: participant_id, trial, choice, response, reward,
    version, reward_c1..reward_c4. Missed trials carry NaN choice/response/reward
    but keep the drifting reward_c columns, exactly as in exp0.csv.
    """

    def __init__(self):
        self.name = "bahrami_2020_arm_exp0"
        self.num_trials = 150
        self.p_miss = 0.034

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            version = int(np.random.choice(VERSIONS))
            prompt = INSTRUCTIONS + "\n"
            for trial in range(self.num_trials):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                t = trial + 1
                cur = PAYOFFS[version][trial]
                row = {
                    "participant_id": participant, "trial": trial,
                    "choice": None, "response": None, "reward": None,
                    "version": version,
                    "reward_c1": cur[0], "reward_c2": cur[1],
                    "reward_c3": cur[2], "reward_c4": cur[3],
                }
                if np.random.rand() < self.p_miss:
                    prompt += (f"\nTrial {t}: You did not respond in time, so the "
                               "trial was skipped and you received no reward.")
                else:
                    prompt += f"\nTrial {t}: You choose machine [HUMAN_RESPONSE]"
                    letter = agent(prompt, choice_options=ARMS)
                    arm = ARMS.index(letter)
                    reward = cur[arm]
                    prompt += f"{letter}[/HUMAN_RESPONSE] and receive {reward} points."
                    row["choice"] = arm + 1
                    row["response"] = arm
                    row["reward"] = reward
                rows.append(row)
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "choice", "response", "reward", "version",
            "reward_c1", "reward_c2", "reward_c3", "reward_c4",
        ])
        return df, prompts


def _random_agent(prompt, choice_options):
    return str(np.random.choice(choice_options))


def main():
    parser = argparse.ArgumentParser(
        description="Smoke-test this simulator with a uniform-random agent.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3,
                        help="number of simulated participants (default: 3)")
    parser.add_argument("--max-chars", type=int, default=None,
                        help="stop each participant at a trial boundary at/past this many chars")
    parser.add_argument("--seed", type=int, default=None,
                        help="numpy random seed, for reproducible runs")
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    task = FourArmBandit()
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
