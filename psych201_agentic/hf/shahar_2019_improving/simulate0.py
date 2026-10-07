# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/shahar_2019_improving``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import random

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp0), with the letter slots kept.
INSTRUCTIONS = (
    "You are playing a game where you try to win as many play pounds as possible; "
    "you get a bonus based on your total. Each round has two stages. In the first "
    "stage you see two first-stage stimuli: press {first_letter} for the first stimulus "
    "or {second_letter} for the second. Your choice moves you to one of two second-stage "
    "states. In the second stage you see two second-stage stimuli in that state: press "
    "{first_letter} for the first stimulus or {second_letter} for the second. "
    "Win as many play pounds as you can."
)


def _letters(pid):
    """Deterministic per-participant A/B mapping, exactly as build_jsonl.py."""
    rng = random.Random(int(pid) * 7919)
    letters = ["A", "B"]
    rng.shuffle(letters)
    return letters[0], letters[1]


class TwoStageTask:
    """Two-stage (two-step) decision task, Shahar et al. (2019), "Improving the
    reliability of model-based decision-making estimates in the two-stage decision
    task with reaction-times and drift-diffusion modeling", PLoS Comput Biol 15(2),
    e1006803.

    Design (Materials and methods, Two-stage decision task, p. 18-19): at each trial
    the participant first chooses one of two first-stage stimuli; a transition then
    moves them to one of two second-stage states (common = 70%, rare = 30%, as in
    Daw et al. 2011), where they choose one of two second-stage stimuli and receive a
    binary reward (0 or 1 play pounds). The task ran for 121 trials at baseline and
    201 trials at follow-up. The reward probability of each of the four second-stage
    bandits drifted slowly and independently (Fig 1B: Gaussian random walk).

    ASSUMPTION: the shipped data encode the transition as 0 = common (70% of stage-1
    rows) and 1 = rare (30%), as the OSF task code ``DDM_RL_TST.m`` does
    (``0-common 1-rare``); the simulator follows the data. The reached state is always
    ``response XOR transition`` (verified on all 174754 stage-1 rows).

    ASSUMPTION: the reward probabilities are shared across participants (a single
    random-walk trajectory per bandit), as the OSF task code ``rndwlk.m`` (boundaries
    [0.2, 0.8], initial values uniform in 0.01 steps, drift 0.025*randn per trial)
    and the tight between-participant reward rates in exp0.csv both indicate. The
    simulator generates one shared walk per session and every simulated participant
    experiences it.

    ASSUMPTION: each session's trial count is the paper's nominal 121 / 201 with a
    ~2% random drop, matching the observed 118-120 / 196-200 blocks in exp0.csv.

    The DataFrame matches exp0.csv minus ``rt``.
    """

    def __init__(self):
        self.name = "shahar_2019_improving_exp0"
        self.nominal_trials = {0: 121, 1: 201}   # baseline / follow-up
        self.drop_prob = 0.02                    # trials omitted (RT filtering etc.)
        self.common_prob = 0.7                   # P(common transition)
        self.reward_lo, self.reward_hi = 0.2, 0.8
        self.reward_step = 0.025

    def _reward_walk(self, num_trials):
        """Shared reward-probability random walk for the 4 second-stage bandits
        (state 0 resp 0, state 0 resp 1, state 1 resp 0, state 1 resp 1)."""
        lo, hi = self.reward_lo, self.reward_hi
        x = np.zeros((4, num_trials))
        x[:, 0] = (np.random.randint(1, int(hi * 100) - int(lo * 100) + 2, 4)
                   + int(lo * 100) - 1) / 100.0
        for i in range(1, num_trials):
            x[:, i] = np.clip(x[:, i - 1] + self.reward_step * np.random.randn(4),
                              lo, hi)
        return x

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        session_names = {0: "first", 1: "second"}
        session_labels = {0: "baseline", 1: "follow_up"}
        walks = {tid: self._reward_walk(self.nominal_trials[tid]) for tid in (0, 1)}
        for participant in tqdm(range(num_simulations)):
            first_letter, second_letter = _letters(participant)
            prompt = INSTRUCTIONS.format(first_letter=first_letter,
                                         second_letter=second_letter) + "\n"
            for task_id in (0, 1):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                num_trials = (self.nominal_trials[task_id]
                              - np.random.binomial(self.nominal_trials[task_id],
                                                   self.drop_prob))
                prompt += f"\nYou begin the {session_names[task_id]} session.\n"
                walk = walks[task_id]
                for block in range(num_trials):
                    if max_chars is not None and len(prompt) >= max_chars:
                        break
                    prompt += "You see two first-stage stimuli. You press [HUMAN_RESPONSE]"
                    letter1 = agent(prompt, choice_options=[first_letter, second_letter])
                    response1 = 0 if letter1 == first_letter else 1
                    transition = 0 if np.random.rand() < self.common_prob else 1
                    second_stage_state = response1 ^ transition
                    state_label = "X" if second_stage_state == 0 else "Y"
                    prompt += (f"{letter1}[/HUMAN_RESPONSE]. The choice moves you to "
                               f"second-stage state {state_label}. ")
                    prompt += "You see two second-stage stimuli. You press [HUMAN_RESPONSE]"
                    letter2 = agent(prompt, choice_options=[first_letter, second_letter])
                    response2 = 0 if letter2 == first_letter else 1
                    bandit = second_stage_state * 2 + response2
                    reward = 1 if np.random.rand() < walk[bandit, block] else 0
                    prompt += (f"{letter2}[/HUMAN_RESPONSE]. You win {reward} play "
                               f"pound{'' if reward == 1 else 's'}.\n")
                    rows.append({
                        "participant_id": participant, "trial": 2 * block, "block": block,
                        "response": response1, "reward": np.nan, "state": 0,
                        "transition": transition, "second_stage_state": second_stage_state,
                        "session": session_labels[task_id], "task_id": task_id,
                        "phase": "test",
                    })
                    rows.append({
                        "participant_id": participant, "trial": 2 * block + 1,
                        "block": block, "response": response2, "reward": float(reward),
                        "state": second_stage_state, "transition": transition,
                        "second_stage_state": second_stage_state,
                        "session": session_labels[task_id], "task_id": task_id,
                        "phase": "test",
                    })
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "block", "response", "reward", "state",
            "transition", "second_stage_state", "session", "task_id", "phase",
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

    task = TwoStageTask()
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