# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 of ``Hugging-Brain/feng_2021_dynamics``, format-identical
to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import random

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_bandit), first block of the transcript.
INSTRUCTIONS = (
    "You are playing a series of games with two slot machines, or bandits, "
    "labeled A and B. Each machine pays out points on each pull. On average, "
    "one machine is always better than the other, but you are not told which "
    "one, and the variability of the payouts is the same for both. Your goal "
    "is to earn as many points as possible. Each game lasts either 5 or 10 "
    "pulls; the number of slots on the bandits shows how long the game is. "
    "The first 4 pulls of every game are instructed: you are told which bandit "
    "to play and cannot play the other. After those, you freely choose which "
    "bandit to play each pull. On free pulls, press A to play Bandit A or "
    "B to play Bandit B.\n"
)


def _label(response, pid):
    """Mirror build_jsonl.py's per-participant A/B token assignment (seeded by pid)."""
    rng = random.Random(int(pid))
    swap = rng.random() < 0.5
    return "B" if (int(response) == 0) == swap else "A"


class HorizonTask:
    """Horizon Task, Experiment "repeater-v1" of Feng, Wang, Zarnescu & Wilson
    (2021), "The dynamics of explore-exploit decisions reveal a signal-to-noise
    mechanism for random exploration", Scientific Reports, 11, 3077.

    Design (Methods, "## Methods": this repeater experiment repeats each game
    across two presentations): participants play 160 distinct games, each
    presented twice (repeatNumber 1/2, gID pairs the two runs), giving 320
    recorded games per participant. Games are 5 or 10 pulls (free horizons 1/6);
    the first 4 pulls are instructed. On each game the means of the two Gaussian
    reward bands are set so one bandit's mean is always 40 or 60 while the other
    is 4/8/12/20/30 points higher or lower; rewards are drawn from a Gaussian
    with the chosen bandit's mean and sd 8, truncated to 1..100 and rounded to
    integers. Games are balanced 1:1 short/long horizon and information
    condition (uc) 1:2:1.

    ASSUMPTION: the paper only describes the per-game means process; the exact
    repeated factorial (20 mean conditions x 8 distinct games, each replayed)
    and the fact that the same gID keeps identical m1/m2/horizon/uc and replays
    the same instructed pulls with the same rewards across its two runs while
    redrawing free-choice outcomes are recovered from exp1.csv. Bandit label
    (A/B) is randomized per participant exactly as in build_jsonl.py. The
    DataFrame matches exp1.csv minus ``rt`` and the demographics columns
    (subjectID/subjectNumber/age/gender).
    """

    def __init__(self):
        self.name = "feng_2021_dynamics_exp1"
        self.bases = (40, 60)
        self.offsets = (4, 8, 12, 20, 30)
        self.games_per_condition = 8       # 20 conditions x 8 distinct games
        self.num_distinct = 160            # each replayed twice -> 320 games
        self.num_games = 320
        self.forced = 4                    # instructed trials at game start
        self.reward_sd = 8.0               # sd of the reward Gaussian
        self.min_reward, self.max_reward = 1, 100
        self.forced_schedule = {1: [0, 0, 0, 1], 2: [0, 0, 1, 1], 3: [0, 1, 1, 1]}

    def _game_specs(self):
        """One entry per distinct game: (gID, m1, m2, horizon, gameLength, uc)."""
        specs = []
        gid = 0
        for base in self.bases:
            for d in self.offsets:
                for sgn in (+1, -1):
                    for i in range(self.games_per_condition):
                        horizon = 1 if i < self.games_per_condition // 2 else 6
                        j = i % (self.games_per_condition // 2)   # uc crossed with horizon
                        if j < 1:
                            uc = 1
                        elif j < 3:
                            uc = 2
                        else:
                            uc = 3
                        means = [base, base + sgn * d]
                        if np.random.rand() < 0.5:
                            m1, m2 = means
                        else:
                            m2, m1 = means
                        specs.append((gid, m1, m2, horizon, horizon + 4, uc))
                        gid += 1
        return specs

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            aid, bid = _label(0, participant), _label(1, participant)
            specs = self._game_specs()
            np.random.shuffle(specs)
            prompt = INSTRUCTIONS
            written = 0
            replay = {}   # gid -> (instructed order, instructed rewards), replayed on repeat 2
            for game in range(self.num_games):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                gid, m1, m2, horizon, glen, uc = specs[game % self.num_distinct]
                repeat = 1 if game < self.num_distinct else 2
                prompt += f"A new game begins. It has {glen} pulls.\n"
                if repeat == 1:
                    forced = list(self.forced_schedule[uc])
                    np.random.shuffle(forced)
                    forced_rewards = []
                else:
                    forced, forced_rewards = replay[gid]
                responses = forced + [None] * horizon
                for trial, response in enumerate(responses):
                    if response is None:
                        prompt += f"Pull {trial + 1}: you choose. You press [HUMAN_RESPONSE]"
                        letter = agent(prompt, choice_options=[aid, bid])
                        response = 0 if letter == aid else 1
                        prompt += f"{letter}[/HUMAN_RESPONSE]. You win "
                    else:
                        letter = _label(response, participant)
                        prompt += (f"Pull {trial + 1}: you are told to play Bandit {letter}. "
                                   f"You win ")
                    mean = m1 if response == 0 else m2
                    if repeat == 2 and trial < self.forced:
                        reward = forced_rewards[trial]
                    else:
                        reward = int(np.clip(round(np.random.normal(mean, self.reward_sd)),
                                             self.min_reward, self.max_reward))
                        if trial < self.forced:
                            forced_rewards.append(reward)
                    prompt += f"{reward} points.\n"
                    rows.append({
                        "participant_id": participant, "trial": trial, "task_id": game,
                        "block": game // 80, "phase": "test",
                        "forced_choice": 1 if trial < self.forced else 0,
                        "response": response, "reward": float(reward),
                        "horizon": horizon, "gameLength": glen, "uc": uc,
                        "m1": m1, "m2": m2, "gID": gid, "repeatNumber": repeat,
                    })
                if repeat == 1:
                    replay[gid] = (forced, forced_rewards)
                written += 1
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "task_id", "block", "phase", "forced_choice",
            "response", "reward", "horizon", "gameLength", "uc", "m1", "m2",
            "gID", "repeatNumber",
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