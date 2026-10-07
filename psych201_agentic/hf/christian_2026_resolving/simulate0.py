# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/christian_2026_resolving``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import random

import numpy as np
import pandas as pd
from tqdm import tqdm

ACTION_ORDER = ["Explore", "Exploit", "Mistake"]
ACTION_RESPONSE = {"Explore": 0, "Exploit": 1, "Mistake": 2}

# Optimal exploration threshold tn (value bound) as a function of the number of
# nights remaining n, per distribution. Copied verbatim from the paper's OSF
# reproducibility archive ``data/optimal_thresholds.csv`` (rows = distribution,
# columns = n = 1..28 nights remaining).
THRESHOLDS = {
    "exponential": {1: 50.0, 2: 63.925, 3: 73.155, 4: 80.175, 5: 85.89, 6: 90.73,
                    7: 94.93, 8: 98.655, 9: 102.005, 10: 105.05, 11: 107.845,
                    12: 110.425, 13: 112.825, 14: 115.075, 15: 117.185, 16: 119.175,
                    17: 121.055, 18: 122.845, 19: 124.55, 20: 126.175, 21: 127.725,
                    22: 129.215, 23: 130.65, 24: 132.025, 25: 133.35, 26: 134.63,
                    27: 135.865, 28: 137.06},
    "triangular": {1: 50.0025, 2: 54.9075, 3: 57.5175, 4: 59.2425, 5: 60.495,
                   6: 61.47, 7: 62.2575, 8: 62.91, 9: 63.465, 10: 63.945, 11: 64.365,
                   12: 64.74, 13: 65.07, 14: 65.3775, 15: 65.6475, 16: 65.895,
                   17: 66.1275, 18: 66.3375, 19: 66.54, 20: 66.72, 21: 66.8925,
                   22: 67.0575, 23: 67.2075, 24: 67.35, 25: 67.485, 26: 67.6125,
                   27: 67.7325, 28: 67.845},
    "power_law": {1: 50.0, 2: 60.355, 3: 68.3025, 4: 75.0, 5: 80.9025, 6: 86.2375,
                  7: 91.145, 8: 95.71, 9: 100.0, 10: 104.0575, 11: 107.915,
                  12: 111.6025, 13: 115.14, 14: 118.5425, 15: 121.825, 16: 125.0,
                  17: 128.0775, 18: 131.065, 19: 133.9725, 20: 136.8025, 21: 139.565,
                  22: 142.26, 23: 144.895, 24: 147.475, 25: 150.0, 26: 152.475,
                  27: 154.905, 28: 157.2875},
    "uniform": {1: 50.0, 2: 58.5786437626905, 3: 63.39745962155613, 4: 66.66666666666666,
                5: 69.09830056250526, 6: 71.01020514433644, 7: 72.57081148225683,
                8: 73.87961250362586, 9: 75.0, 10: 75.97469266479577, 11: 76.833752096446,
                12: 77.59907622602041, 13: 78.28707270446674, 14: 78.91032779404661,
                15: 79.47869038423275, 16: 80.0, 17: 80.48058983988963, 18: 80.92564301694539,
                19: 81.33945031366294, 20: 81.72560023684431, 21: 82.0871215252208,
                22: 82.42659161988843, 23: 82.74622034857855, 24: 83.04791528014628,
                25: 83.33333333333334, 26: 83.60392194562885, 27: 83.86095222035911,
                28: 84.105545843966},
}

# Empirical distribution of comprehension-quiz attempt failures (per participant),
# recovered from exp0.csv (values -> participant counts).
QUIZ_FAILURES = {0: 2005, 1: 389, 2: 79, 3: 16, 4: 7, 5: 10, 6: 2, 7: 4, 8: 1,
                 9: 2, 10: 2, 13: 1, 15: 1, 23: 1}
QUIZ_VALUES = sorted(QUIZ_FAILURES)
QUIZ_PROBS = np.array([QUIZ_FAILURES[v] for v in QUIZ_VALUES], dtype=float)
QUIZ_PROBS /= QUIZ_PROBS.sum()

# Instruction / narration template mirroring build_jsonl.py's transcribe_exp0
# exactly, with the per-participant letter slots kept.
INSTRUCTION_HEAD = (
    "You are about to spend {total_nights} nights in a new city. Restaurants in "
    "the city vary in quality: you cannot know a restaurant's quality until you "
    "visit it, and once you visit it its quality never changes. Quality scores are "
    "distributed randomly with a mean of 50. Before your trip you saw 84 sample "
    "scores from this city to get a sense of how scores are distributed. Your goal "
    "is to maximize the total score of the restaurants you visit across all your "
    "nights, and you will earn a bonus proportional to your total score.\n"
    "On each of the {total_nights} nights you choose a restaurant. On every night "
    "respond with a single letter: press {explore} to visit a NEW restaurant you "
    "have not been to before, press {exploit} to return to the BEST restaurant you "
    "have found so far, or press {mistake} to return to some other restaurant you "
    "have already visited.\n"
)

NARRATION = {
    "Explore": "You visit a new restaurant; its score is {reward}.",
    "Exploit": "You return to your best restaurant; its score is {reward}.",
    "Mistake": "You return to a previously visited restaurant; its score is {reward}.",
}


class RestaurantProblem:
    """Feynman's restaurant problem, Experiment 1 of Christian, Russek, &
    Griffiths (2026), "Resolving Feynman's restaurant problem reveals optimal
    solutions and human strategies", PNAS, 123(23), e2509612123.

    Design (Materials and Methods, Experimental Procedure): each participant
    plays a single sequence of T nights (T in {7,14,28}), choosing each night to
    Explore a new restaurant, Exploit the best seen so far, or return to some
    other seen restaurant (a Mistake). Hidden restaurant values are drawn from
    one of four between-subject distributions (Uniform[0,100]; Triangular on
    [0,75] with density proportional to x; Exponential rescaled to mean 50;
    Power-law x~2/x^3 on [1,inf) rescaled to mean 50), each rescaled to mean 50.

    Clamping: for the first floor(clamp*T/7) nights (clamp in 0..6), a new
    restaurant's value is truncated to the range [0, tn), where tn is the
    optimal exploration threshold for the current nights remaining (from the
    OSF optimal_thresholds.csv), so values never exceed tn during that window.

    ASSUMPTION: value rounding — restaurant values are stored as integers
    (observed in the data); draws are rounded to the nearest integer.
    ASSUMPTION: quiz_failures is exogenous to the task; it is sampled from the
    empirical distribution of quiz_failures observed in exp0.csv.
    ASSUMPTION: on the first night (no restaurant visited yet) and while no
    seen-but-not-best restaurant exists, only the valid choices are offered to
    the agent (Explore alone on night 1; Explore/Exploit while the only seen
    restaurant is also the best). This matches the observed data, where night 1
    is always Explore and Mistake requires a seen-but-not-best restaurant.
    ASSUMPTION: the paper notes a numerical error made the Exponential clamping
    bound slightly too high (observed as a few clamped Exponential rewards
    exceeding tn). This simulator uses the exact thresholds from
    optimal_thresholds.csv and does not reproduce that error.

    The DataFrame matches exp0.csv (all columns, since the transcription reads
    them from the CSV); rt and other trial-level timing columns are absent from
    the source.
    """

    def __init__(self):
        self.name = "christian_2026_resolving_exp0"
        self.total_nights_options = [7, 14, 28]
        self.conditions = ["triangular", "uniform", "exponential", "power_law"]
        self.clamp_options = list(range(7))

    @staticmethod
    def _draw_value(condition):
        """Draw one (unclamped) restaurant value from the given distribution."""
        u = np.random.random()
        if condition == "uniform":
            return int(np.round(100.0 * u))
        if condition == "triangular":
            return int(np.round(75.0 * np.sqrt(u)))
        if condition == "exponential":
            return int(np.round(-50.0 * np.log(max(u, 1e-12))))
        # power_law: X = 25 * Y, Y ~ 2 y^-3 on [1, inf)
        y = 1.0 / np.sqrt(max(1.0 - u, 1e-12))
        return int(np.round(25.0 * y))

    def _draw_restaurant(self, condition, clamped, tn):
        """Draw a restaurant value, truncating to [0, tn) when clamped."""
        while True:
            v = self._draw_value(condition)
            if not clamped or v < tn:
                return v

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            pid = participant
            total_nights = int(np.random.choice(self.total_nights_options))
            condition = str(np.random.choice(self.conditions))
            clamp = int(np.random.choice(self.clamp_options))
            quiz_failures = int(np.random.choice(QUIZ_VALUES, p=QUIZ_PROBS))

            # per-participant A/B/C mapping, exactly as in build_jsonl.py
            letters = ["A", "B", "C"]
            rng = random.Random(pid)
            rng.shuffle(letters)
            mapping = dict(zip(ACTION_ORDER, letters))

            prompt = INSTRUCTION_HEAD.format(
                total_nights=total_nights,
                explore=mapping["Explore"],
                exploit=mapping["Exploit"],
                mistake=mapping["Mistake"],
            )

            num_clamped = int(clamp * total_nights / 7)
            visited = []
            for trial in range(total_nights):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                nights_remaining = total_nights - trial
                best_known = max(visited) if visited else np.nan

                valid_actions = ["Explore"]
                if visited:
                    valid_actions.append("Exploit")
                if visited and any(v < max(visited) for v in visited):
                    valid_actions.append("Mistake")
                options = [mapping[a] for a in valid_actions]

                prompt += (f"Night {trial + 1} of {total_nights}, {nights_remaining} "
                           "night(s) remaining. ")
                if pd.isna(best_known):
                    prompt += "You have not visited any restaurant yet. "
                else:
                    prompt += f"Your best score so far is {int(best_known)}. "
                prompt += "You press [HUMAN_RESPONSE]"
                letter = agent(prompt, choice_options=options)
                action = [a for a in ACTION_ORDER if mapping[a] == letter][0]

                if action == "Explore":
                    tn = THRESHOLDS[condition][nights_remaining]
                    reward = self._draw_restaurant(condition,
                                                   trial < num_clamped, tn)
                    visited.append(reward)
                elif action == "Exploit":
                    reward = int(best_known)
                else:  # Mistake: return to a seen-but-not-best restaurant
                    non_best = [v for v in visited if v < max(visited)]
                    reward = int(np.random.choice(non_best))

                prompt += (f"{letter}[/HUMAN_RESPONSE]. "
                           + NARRATION[action].format(reward=reward) + "\n")

                rows.append({
                    "participant_id": pid, "trial": trial,
                    "response": ACTION_RESPONSE[action],
                    "total_nights": total_nights,
                    "nights_remaining": nights_remaining,
                    "action": action,
                    "best_known": best_known,
                    "reward": reward,
                    "clamp": clamp,
                    "quiz_failures": quiz_failures,
                    "condition": condition,
                    "valid": 1 if action != "Mistake" else 0,
                })
            prompts.append(prompt.strip())

        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "total_nights",
            "nights_remaining", "action", "best_known", "reward", "clamp",
            "quiz_failures", "condition", "valid",
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
                        help="stop each participant at the block boundary at/past this many chars")
    parser.add_argument("--seed", type=int, default=None,
                        help="numpy random seed, for reproducible runs")
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    task = RestaurantProblem()
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
