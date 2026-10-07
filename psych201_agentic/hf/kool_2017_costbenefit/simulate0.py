# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/kool_2017_costbenefit``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or
import the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

EXP0_INSTR = (
    "You are flying a spaceship between planets to collect space treasure. "
    "At the start of every round a cue shows the stakes for that round: all points "
    "earned are multiplied by 1 (low stakes) or by 5 (high stakes). "
    "You begin in one of two starting points; each shows a different pair of "
    "spaceships side by side. One spaceship of each pair always flies to one of the "
    "two planets, and the other always flies to the other planet. "
    "Press F to choose the left spaceship and J to choose the right. "
    "You then fly to that planet, where an alien works in a space mine; press the "
    "space bar within the time limit to collect the treasure it pays out. The alien "
    "is sometimes in a good part of the mine (paying many pieces, up to 9) and "
    "sometimes in a bad spot (fewer pieces); these amounts drift slowly over the "
    "session. Your points this round are the pieces of treasure times the round's "
    "stake multiplier, added to your running score in the top-right corner."
)


def _reflect(v):
    """Reflect an integer scalar reward back into [0, 9] (the paper's
    reflecting bounds on the drifting rewards)."""
    v = int(round(v))
    while True:
        if v < 0:
            v = -v
        elif v > 9:
            v = 18 - v
        else:
            return v


class TwoStepCostBenefitExp0:
    """Experiment 1 of Kool, Gershman & Cushman (2017), "Cost-benefit
    arbitration between multiple reinforcement-learning systems",
    Psychological Science, 28(9), 1321-1333.

    Design (Materials and procedure, p. 1323-1325; Fig. 1): two-step task with
    two first-stage states. State 0 shows spaceships {1,2}, state 1 shows
    spaceships {3,4}; a given spaceship always flies to the same planet
    (1 -> planet 1, 2 -> planet 2, 3 -> planet 1, 4 -> planet 2), with either
    planet reachable from each starting state. Each planet pays a scalar reward
    (0..9 pieces of treasure) that drifts as a Gaussian random walk
    (Gaussian, mean 0, sigma 2) with reflecting bounds at 0 and 9; one planet
    is initialized low (0..4) and the other high (5..9). Each trial starts in a
    random first-stage state, the pair of ships is placed left/right at random,
    and a per-trial stake cue (x1 or x5, ~50% high) multiplies the points
    earned. Participants completed 25 practice + 200 rewarded (test) trials;
    the practice phase has no response deadline, the test phase a 1500 ms
    deadline for the F/J first-stage choice and the space-bar reward press.

    DataFrame matches exp0.csv minus demographics / model-fit / RT / keycode /
    timing columns.

    ASSUMPTION: in the shipped data the practice phase always has stake 1 (no
    high-stakes practice trials); test stakes are ~49% high.
    ASSUMPTION: first-stage timeouts (468) and space-bar timeouts (580) occur
    only in the test phase; this simulator uses the same per-trial rates
    (468/(102*200) and 580/(102*200-468)). A first-stage timeout leaves reward 0
    and the score unchanged; a space-bar timeout delivers 0 pieces instead of
    the planet's current value.
    ASSUMPTION: ``score`` resets at the practice -> test boundary (the CSV's
    running score is a per-phase total). reward == rews of the reached planet is
    given in "pieces"; points = reward * stake; score += points.
    ASSUMPTION: ships always occupy state 0 (ships 1,2) and state 1 (ships 3,4)
    with the fixed ship->planet mapping above; left/right is randomized per
    trial, matching exp0.csv.
    """

    def __init__(self):
        self.name = "kool_2017_costbenefit_exp0"
        self.num_practice = 25
        self.num_test = 200
        self.ships_by_state = {0: [1, 2], 1: [3, 4]}
        self.ship_to_planet = {1: 1, 2: 2, 3: 1, 4: 2}
        self.reward_sd = 2.0
        self.p_timeout = 468.0 / (102 * 200)
        self.p_spacebar = 580.0 / (102 * 200 - 468)

    def _step(self, v):
        return _reflect(v + np.random.normal(0.0, self.reward_sd))

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            pid = f"Sub{participant + 1}"
            rews = {1: 0, 2: 0}
            low_planet = 1 if np.random.rand() < 0.5 else 2
            rews[low_planet] = np.random.randint(0, 5)
            rews[3 - low_planet] = np.random.randint(5, 10)
            prompt = EXP0_INSTR
            score = 0
            for t in range(self.num_practice + self.num_test):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                trial_nr = t if t < self.num_practice else t - self.num_practice
                phase = "practice" if t < self.num_practice else "test"
                stake = 1 if phase == "practice" else (5 if np.random.rand() < 0.5 else 1)
                rews[1] = self._step(rews[1])
                rews[2] = self._step(rews[2])
                state = 0 if np.random.rand() < 0.5 else 1
                state1 = state + 1
                ships = self.ships_by_state[state]
                if np.random.rand() < 0.5:
                    stim_left, stim_right = ships
                else:
                    stim_right, stim_left = ships
                timed_out = phase == "test" and np.random.rand() < self.p_timeout
                if timed_out:
                    response = np.nan
                    valid, state2 = 0, np.nan
                    reward, points = 0, 0
                    text = (f"\nStakes x{stake}. You fail to respond within the time "
                            f"limit, so no reward. Your running score is {score}.")
                else:
                    prompt += (f"\nStakes x{stake}. Two spaceships appear: Ship {stim_left} "
                               f"on the left and Ship {stim_right} on the right. "
                               f"You press [HUMAN_RESPONSE]")
                    response = 0 if agent(prompt, choice_options=["F", "J"]) == "F" else 1
                    valid = 1
                    choice1 = stim_left if response == 0 else stim_right
                    state2 = self.ship_to_planet[choice1]
                    reward = 0 if (phase == "test" and np.random.rand() < self.p_spacebar) else rews[state2]
                    points = reward * stake
                    score += points
                    text = (f"{'F' if response == 0 else 'J'}"
                            f"[/HUMAN_RESPONSE]. You fly to Planet {state2}. "
                            f"The alien there gives {reward} pieces of treasure, worth "
                            f"{points} points. Your running score is {score}.")
                prompt += text
                rows.append({
                    "participant_id": pid, "trial": t, "block": t,
                    "phase": phase, "state": state, "response": response,
                    "valid": valid, "reward": reward, "state1": state1,
                    "stim_left": stim_left, "stim_right": stim_right,
                    "state2": state2, "stake": stake, "score": score,
                    "practice": 1 if phase == "practice" else 0,
                    "rews_s1": rews[1], "rews_s2": rews[2], "trial_nr": trial_nr,
                })
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "block", "phase", "state", "response",
            "valid", "reward", "state1", "stim_left", "stim_right", "state2",
            "stake", "score", "practice", "rews_s1", "rews_s2", "trial_nr",
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

    task = TwoStepCostBenefitExp0()
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
    print(prompts[0][-400:])


if __name__ == "__main__":
    main()