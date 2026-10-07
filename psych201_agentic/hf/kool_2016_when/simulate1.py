# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 (novel two-step) of ``Hugging-Brain/kool_2016_when``,
format-identical to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import hashlib
import random

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (INSTR1).
INSTRUCTIONS = (
    "You are an astronaut flying a spaceship from Earth to collect space treasure on two "
    "different planets. Each planet has one alien on it, and each alien has its own space "
    "treasure mine. A mine can contain space treasure (which gives positive points) or "
    "antimatter (which gives negative points). The quality of each mine drifts slowly over "
    "time, so you must keep paying attention. On each trial, one of two pairs of spaceships "
    "appears. Choose one spaceship of the pair by pressing A or B. In each pair, one "
    "spaceship always flies to one planet and the other always flies to the other planet. "
    "When you arrive at a planet, one alien is there. Press the space bar to ask the alien "
    "to mine. You then learn how many points of space treasure (or antimatter) you received. "
    "First you play practice trials with no time limit. Then the real game starts, with 2 "
    "seconds to make each choice. Press A or B to choose the option you want."
)

# Verbatim from build_jsonl.py (BOUNDARY): shown once between practice and test.
BOUNDARY = (
    "The practice trials are over. In the real game you will find new planets, new aliens "
    "and new mines, but the rules and the spaceships are the same."
)

PAIR = {1: "first", 2: "second"}  # first-stage state -> which spaceship pair appeared

# (practice?, state2) -> planet color, as in build_jsonl.PLANET.
PLANET = {
    (True, 1): "green",
    (True, 2): "yellow",
    (False, 1): "purple",
    (False, 2): "red",
}


def _rng(seed_str):
    digest = hashlib.md5(seed_str.encode("utf-8")).hexdigest()
    return random.Random(int(digest, 16) % (2 ** 32))


def _letter_map(rng):
    letters = ["A", "B"]
    rng.shuffle(letters)
    return {0: letters[0], 1: letters[1]}


class NovelTwoStep:
    """Kool, Cushman & Gershman (2016), PLoS Comput Biol, Experiment 2: the
    novel two-step task.

    Design (Experimental methods > Novel paradigm, p. 21): 25 self-paced
    practice trials then 125 timed (2 s) trials. Each trial starts randomly in
    one of two first-stage states; the participant makes a single free choice
    between a pair of spaceships (A/B). The transition is deterministic:
    choosing the lower-numbered rocket (response 0) of the current state leads
    to planet 1 (state2=1), the higher (response 1) to planet 2 (state2=2).
    At the reached planet a confirmatory spacebar press (forced, not a choice)
    yields a reward magnitude (integer -4..5). Two reward magnitudes drift per
    an integer Gaussian random walk (sigma=2) with reflecting bounds -4..+5;
    one is initialized negative (-4..-1) and the other positive (+1..+5).

    ASSUMPTION: reward magnitudes are re-initialized at the practice/test
    boundary, matching exp0's per-phase fresh reward process.
    ASSUMPTION: the confirmatory spacebar is always pressed (no stage-2
    timeout simulated); rt2 is set to a fixed dummy value (1000) so
    build_jsonl.py's narration branch is the press, never the miss.
    ASSUMPTION: the letter->identity mapping is regenerated exactly as
    build_jsonl.py does (md5-seeded from the participant id; one A/B map per
    participant shared by both spaceship pairs), so the round trip through
    build_jsonl.py is byte-identical.

    The DataFrame matches exp1.csv minus the columns a text simulator cannot
    produce (rt, rt1, choice1, trial_number, time_elapsed, age, gender,
    score_final, time_total_ms, rews*).
    """

    def __init__(self):
        self.name = "kool_2016_when_exp1"
        self.num_practice = 25
        self.num_test = 125
        self.walk_sigma = 2.0
        self.bounds = (-4, 5)

    def _fresh_rews(self, rng):
        neg = rng.randint(-4, -1)
        pos = rng.randint(1, 5)
        if rng.random() < 0.5:
            return {1: neg, 2: pos}
        return {1: pos, 2: neg}

    def _step_rews(self, v, rng):
        v = v + int(round(rng.gauss(0.0, self.walk_sigma)))
        lo, hi = self.bounds
        while v < lo:
            v = 2 * lo - v
        while v > hi:
            v = 2 * hi - v
        return v

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for sim in tqdm(range(num_simulations)):
            pid = f"sim{sim}"
            rng = _rng(f"kool2016-exp1-{pid}")
            # one A/B map per participant, shared by both first-stage states,
            # as in build_jsonl.py.
            lm = _letter_map(rng)
            letters = {1: lm, 2: lm}

            rews = self._fresh_rews(rng)
            prompt = INSTRUCTIONS
            score = 0
            for block in range(self.num_practice + self.num_test):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                phase = "practice" if block < self.num_practice else "test"
                if block == self.num_practice:
                    rews = self._fresh_rews(rng)
                    prompt += f"\n{BOUNDARY}"

                state1 = 1 if rng.random() < 0.5 else 2
                opts = list(letters[state1].values())
                prompt += (f"\nYou see the {PAIR[state1]} pair of spaceships. "
                           "You press [HUMAN_RESPONSE]")
                letter = agent(prompt, choice_options=opts)
                resp = next(k for k, v in letters[state1].items() if v == letter)
                prompt += f"{letter}[/HUMAN_RESPONSE]."

                state2 = resp + 1  # deterministic transition
                planet = PLANET[(phase == "practice", state2)]
                prompt += (f" You travel to the {planet} planet. "
                           "You press the space bar to mine.")
                reward = rews[state2]
                if reward > 0:
                    prompt += f" You gain {reward} points of space treasure."
                elif reward < 0:
                    prompt += f" You gain {abs(reward)} points of antimatter."
                else:
                    prompt += " You gain no points."
                score += reward

                rows.append({
                    "participant_id": pid, "block": block, "trial": block,
                    "phase": phase, "response": float(resp), "state": state1 - 1,
                    "reward": reward, "valid": 1, "state1": state1, "state2": state2,
                    "choice1": (state1 - 1) * 2 + resp + 1, "rt2": 1000, "score": score,
                })

                rews[1] = self._step_rews(rews[1], rng)
                rews[2] = self._step_rews(rews[2], rng)
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "block", "trial", "phase", "response", "state",
            "reward", "valid", "state1", "state2", "choice1", "rt2", "score",
        ])
        return df, prompts


def _random_agent(prompt, choice_options):
    return str(np.random.choice(choice_options))


def main():
    parser = argparse.ArgumentParser(
        description="Smoke-test this simulator with a uniform-random agent.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3)
    parser.add_argument("--max-chars", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()
    if args.seed is not None:
        np.random.seed(args.seed)

    task = NovelTwoStep()
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