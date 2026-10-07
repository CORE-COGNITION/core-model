# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/sadeghiyeh_2020_temporal``
(Horizon Task, two-armed bandit games), format-identical to the repo's
``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import json

import numpy as np
import pandas as pd

# Verbatim from build_jsonl.py (transcribe_exp0).
INSTRUCTIONS = (
    "You will play a series of games, each featuring two slot machines: "
    "Machine A and Machine B. Each machine pays out points drawn from a "
    "bell-shaped distribution, but you are not told the average payout of "
    "either machine and it changes from game to game; one machine is better "
    "on average, and you can only find out which by playing them. Your goal "
    "is to win as many points as possible. Each game begins with four forced "
    "draws, in which the computer tells you which machine to play, so you can "
    "learn about their payoffs. After the forced draws come free draws, in "
    "which you choose for yourself. Games have either 1 or 6 free draws. On "
    "each free draw, press A to play Machine A or press B to play Machine B, "
    "and then you will see how many points you won.\n"
)


class HorizonTask:
    """Horizon Task (two-armed bandit), Experiment 1 of Sadeghiyeh et al.
    (2020), "Temporal discounting correlates with directed exploration but not
    with random exploration", Sci Rep, 10, 4020.

    Design (Methods, "Horizon task", pp. 3-4): 256 allocated game slots, of
    which each subject actually plays the ones reachable in their session
    (observed 25-160 played games; the simulator defaults to the full 160-game
    session). Each game is a fresh pair of one-armed bandits whose payoff means
    are fixed for that game and whose reward is drawn from a Gaussian with
    standard deviation fixed at 8 points. The first four draws of every game
    are experimenter-instructed ("forced"); the remaining trials are free
    choices. Games have either 1 (short, 5 trials total) or 6 (long, 10
    trials) free draws. Forced trials come in an unequal-information block
    (one bandit forced once, the other three times; the "[1 3] condition")
    or an equal-information block (each bandit forced twice; the "[2 2]
    condition"), in random order.

    The transcript narration (build_jsonl.py::transcribe_exp0) is mirrored
    exactly: forced draws are plain narration, free draws are marked with the
    chosen machine letter plus the points won.

    ASSUMPTION: the paper fixes reward S.D. at 8 points but does not give the
    means schedule or any bounds. From exp0.csv the two means take the 30
    observed (mean_A, mean_B) pairs: an anchor mean of 40 or 60 plus an offset
    of +-4, 8, 12 or 20, with the A/B assignment randomised; this is the
    generative rule implemented here. Rewards are integers (observed residual
    SD = 8.09, min = 1, max = 99), so the simulator uses
    reward = clip(round(N(mean, 8)), 1, 99).

    ASSUMPTION: the data show information conditions and horizons each
    balanced ~50/50 across games, so they are sampled uniformly.

    ASSUMPTION: the "correct" column of exp0.csv is 1 iff the chosen bandit's
    scheduled reward >= the alternative bandit's scheduled reward at that
    trial position (ties count as correct; the README's "more than" is off by
    exactly the 1153 tied draws). correct_total counts correct free draws
    only, and accuracy_game = correct_total / horizon, matching the source.

    The DataFrame matches exp0.csv minus ``rt``, ``gID`` and the timing
    columns (``time_bandit_on``, ``time_press_key``, ``time_reward_on``,
    ``delta_time_press_key``).
    """

    def __init__(self, num_games=160):
        self.name = "sadeghiyeh_2020_temporal_exp0"
        self.num_games = num_games
        self.reward_sd = 8.0
        self.reward_min = 1
        self.reward_max = 99
        self.anchors = [40, 60]
        self.diffs = [4, 8, 12, 20]

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in range(num_simulations):
            prompt = INSTRUCTIONS
            for game in range(self.num_games):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                horizon = int(np.random.choice([1, 6]))
                game_length = horizon + 4
                anchor = int(np.random.choice(self.anchors))
                diff = int(np.random.choice(self.diffs))
                sign = int(np.random.choice([-1, 1]))
                m1, m2 = anchor, anchor + sign * diff
                if np.random.rand() < 0.5:
                    m1, m2 = m2, m1
                mean_A, mean_B = m1, m2
                if np.random.rand() < 0.5:
                    # [1 3] condition: one bandit forced once, the other thrice
                    singleton = int(np.random.choice([1, 2]))
                    forced_seq = [singleton] + [3 - singleton] * 3
                else:
                    # [2 2] condition: each bandit forced twice
                    forced_seq = [1, 1, 2, 2]
                np.random.shuffle(forced_seq)
                forced_seq = [int(x) for x in forced_seq]
                rewards = []
                for m in (mean_A, mean_B):
                    draws = np.round(np.random.normal(
                        m, self.reward_sd, game_length)).astype(int)
                    rewards.append(np.clip(draws, self.reward_min,
                                           self.reward_max).tolist())

                prompt += (f"\nGame {game + 1}. Two machines (A and B); this "
                           f"game has {horizon} free draw(s).\n")
                correct_total = 0
                for trial in range(game_length):
                    forced = trial < 4
                    if forced:
                        band = forced_seq[trial] - 1
                        machine = "A" if band == 0 else "B"
                        reward = rewards[band][trial]
                        prompt += (f"You are instructed to play Machine "
                                   f"{machine}. You win {reward} points.\n")
                    else:
                        prompt += "You press [HUMAN_RESPONSE]"
                        letter = agent(prompt, choice_options=["A", "B"])
                        band = 0 if letter == "A" else 1
                        reward = rewards[band][trial]
                        prompt += (f"{letter}[/HUMAN_RESPONSE]. You win "
                                   f"{reward} points.\n")
                        correct_total += int(
                            reward >= rewards[1 - band][trial])
                    correct = int(reward >= rewards[1 - band][trial])
                    rows.append({
                        "participant_id": participant, "task_id": game,
                        "trial": trial, "horizon": horizon, "phase": "test",
                        "forced_choice": 1 if forced else 0,
                        "response": band, "reward": reward,
                        "correct": correct, "key": band + 1,
                        "forced_trial": forced_seq[trial] if forced else 0,
                        "mean_A": mean_A, "mean_B": mean_B,
                        "mean_offered": json.dumps([mean_A, mean_B]),
                        "rewards_schedule": json.dumps(rewards),
                        "game_length": game_length, "nfree": horizon,
                        "nforced": json.dumps(forced_seq),
                        "correct_total": correct_total,
                        "accuracy_game": correct_total / horizon,
                    })
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "task_id", "trial", "horizon", "phase",
            "forced_choice", "response", "reward", "correct", "key",
            "forced_trial", "mean_A", "mean_B", "mean_offered",
            "rewards_schedule", "game_length", "nfree", "nforced",
            "correct_total", "accuracy_game",
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

    task = HorizonTask()
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