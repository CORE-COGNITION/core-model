# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/thoma_2025_emerging``,
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
    "You are helping find zoo animals that have escaped and are hiding behind two "
    "houses. The experimenter shows you 50 escaped animals on a sheet and explains "
    "that you should find as many as possible by guessing which house an animal is "
    "hiding behind. There are two identical houses, a left house and a right house. "
    "On each trial, press {left} to choose the left house or press "
    "{right} to choose the right house. "
    "After each choice the houses turn transparent so you can see exactly where "
    "animals are hiding, and a checkmark or a cross shows whether your choice was "
    "correct. Every correct choice fills one tenth of a blue circle in the corner; "
    "each full circle earns you a token.\n"
)

CONDITIONS = ["static_high", "static_random", "ecol_dyn"]
AGE_GROUPS = ["3-4 years", "6-7 years", "9-11 years", "adult"]
# plausible per-age-group central ages, only used to fill constant demographics
AGE_CENTERS = {"3-4 years": 4.0, "6-7 years": 6.5, "9-11 years": 10.0, "adult": 26.0}
EDUCATION = ["Nicht zutreffend", "Kindergarten", "Grundschule",
             "Weiterführende Schule", "Abitur"]


def _mapping_for(pid):
    """Same deterministic per-participant left/right -> letter as build_jsonl.py."""
    if str(pid).isdigit():
        h = int(str(pid).replace("-", ""))
    else:
        h = sum(map(ord, str(pid)))
    if h % 2 == 0:
        return {"left": "A", "right": "B"}
    return {"left": "B", "right": "A"}


class ProbabilityLearningTask:
    """Child-friendly two-option probability-learning task, Thoma, Newell, &
    Schulze (2025), "Emerging adaptivity in probability learning", JEP:General,
    154(6), 1523-1544, Experiment 1.

    Design (Design & Method, pp. 8-11): 100 trials in 5 blocks of 20, between
    two houses (left/right), one of three between-subjects statistical
    environments. static_high: the majority (high-probability) option yields a
    reward on 70% of trials, the other on 30%, mutually exclusive (exactly one
    side scheduled), collected immediately. static_random: each option yields a
    reward on 50% of trials, mutually exclusive. ecol_dyn: a reward-hold
    mechanism (Ellerby & Tunney 2019; Schulze et al. 2017) — each side is
    independently scheduled (majority 70%, minority 30%); an uncollected
    scheduled reward stays on hold (target) until collected, so the outcome
    probability rises over trials while an option is left unchosen. Whether a
    reward is delivered equals whether the chosen side's target is set.

    ASSUMPTION: scheduled (target) draws are independent per trial/side;
    the hold keeps a scheduled-but-uncollected reward as the side's target until
    that side is chosen (verified 100% against all 161 ecol_dyn participants).
    ASSUMPTION: static_random's majority_location is set to 1 for all
    participants as in the data (both sides are equally probable, so it is
    inert). ASSUMPTION: demographics (age_group/age/gender/education/grade) and
    the post-hoc estimates (estimate_ml/estimate_left/estimate_right) are
    plausible constants sampled per participant; they are repeated on every row
    but do not affect the narration.

    The DataFrame matches exp0.csv's 21-column schema exactly (no columns
    dropped).
    """

    def __init__(self):
        self.name = "thoma_2025_emerging_exp0"
        self.num_trials = 100       # total trials per participant
        self.trials_per_block = 20
        self.p_high = 0.7           # scheduled prob of the majority option
        self.p_low = 0.3            # scheduled prob of the minority option

    def _condition_params(self, condition, majority_location):
        """Return (p_left, p_right): probability each side is scheduled."""
        if condition == "static_high":
            return ((self.p_high, self.p_low) if majority_location == 0
                    else (self.p_low, self.p_high))
        if condition == "static_random":
            return (0.5, 0.5)
        # ecol_dyn: same programmed probs as static_high
        return ((self.p_high, self.p_low) if majority_location == 0
                else (self.p_low, self.p_high))

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            condition = str(np.random.choice(CONDITIONS))
            age_group = str(np.random.choice(AGE_GROUPS))
            gender = str(np.random.choice(["f", "m"]))
            education = str(np.random.choice(EDUCATION))
            grade = str(np.random.randint(0, 7))
            if condition == "static_random":
                majority_location = 1
            else:
                majority_location = int(np.random.rand() < 0.5)
            pid = 1000 + participant
            mapping = _mapping_for(pid)
            prompt = INSTRUCTIONS.format(left=mapping["left"], right=mapping["right"])

            # per-side held (uncollected scheduled) reward state for ecol_dyn
            hold_left, hold_right = 0, 0
            # post-hoc estimate per participant (inert in narration)
            estimate_ml = int(np.random.rand() < 0.5)
            estimate_left = int(np.random.uniform(0, 51))
            estimate_right = int(100 - estimate_left)

            last_block = -1
            for trial in range(self.num_trials):
                block = trial // self.trials_per_block
                if block != last_block:
                    if max_chars is not None and len(prompt) >= max_chars:
                        break
                    prompt += f"\nBlock {block + 1} begins.\n"
                    last_block = block
                p_left, p_right = self._condition_params(condition, majority_location)
                scheduled_left = int(np.random.rand() < p_left)
                scheduled_right = int(np.random.rand() < p_right)
                if condition == "ecol_dyn":
                    target_left = int(scheduled_left or hold_left)
                    target_right = int(scheduled_right or hold_right)
                else:
                    target_left = scheduled_left
                    target_right = scheduled_right
                prompt += "You tap [HUMAN_RESPONSE]"
                letter = agent(prompt, choice_options=[mapping["left"], mapping["right"]])
                side = "left" if letter == mapping["left"] else "right"
                response = 0 if side == "left" else 1
                chosen_target = target_left if response == 0 else target_right
                reward = int(chosen_target == 1)
                # update reward-hold bookkeeping (ecol_dyn)
                if condition == "ecol_dyn":
                    hold_left = int(target_left == 1 and response != 0)
                    hold_right = int(target_right == 1 and response != 1)

                left_state = ("an animal is behind the left house" if target_left
                              else "no animal behind the left house")
                right_state = ("an animal is behind the right house" if target_right
                               else "no animal behind the right house")
                found = ("You find an animal (checkmark)" if reward == 1
                         else "You find no animal (cross)")
                prompt += (
                    f"{letter}[/HUMAN_RESPONSE] "
                    f"(the {side} house). {found} - {left_state}; {right_state}.\n"
                )
                ml_correct = int(majority_location == response)
                rows.append({
                    "participant_id": pid, "condition": condition,
                    "age_group": age_group, "age": AGE_CENTERS[age_group],
                    "gender": gender, "education": education, "grade": grade,
                    "trial": trial, "block": block,
                    "majority_location": majority_location,
                    "scheduled_left": scheduled_left,
                    "scheduled_right": scheduled_right,
                    "target_left": target_left, "target_right": target_right,
                    "keypress": side, "response": response, "reward": reward,
                    "ml_correct": ml_correct, "estimate_ml": estimate_ml,
                    "estimate_left": estimate_left,
                    "estimate_right": float(estimate_right),
                })
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "condition", "age_group", "age", "gender",
            "education", "grade", "trial", "block", "majority_location",
            "scheduled_left", "scheduled_right", "target_left", "target_right",
            "keypress", "response", "reward", "ml_correct", "estimate_ml",
            "estimate_left", "estimate_right",
        ])
        df["grade"] = df["grade"].astype(str)
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

    task = ProbabilityLearningTask()
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