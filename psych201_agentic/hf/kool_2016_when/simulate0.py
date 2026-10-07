# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 (Daw two-step) of ``Hugging-Brain/kool_2016_when``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import hashlib
import random

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (INSTR0).
INSTRUCTIONS = (
    "You are an astronaut flying a spaceship from Earth to collect space treasure on two "
    "different planets. Each planet has two aliens on it, and each alien has its own space "
    "treasure mine. If an alien has a good mine, it is likely to share a piece of space "
    "treasure with you; if its mine is bad, it usually will not. The quality of each mine "
    "drifts slowly over time, so you must keep paying attention. On each trial, two "
    "spaceships appear. Choose one by pressing A or B. Each spaceship mostly flies to one of "
    "the planets and sometimes to the other; this does not change during the game. When you "
    "arrive at a planet, two aliens appear. Choose one by pressing A or B to ask it for "
    "treasure. You then learn whether you found space treasure (worth 1 point) or not (0 "
    "points). First you play practice trials with no time limit. Then the real game starts, "
    "with 2 seconds to make each choice. Press A or B to choose the option you want."
)

# Verbatim from build_jsonl.py (BOUNDARY): shown once between practice and test.
BOUNDARY = (
    "The practice trials are over. In the real game you will find new planets, new aliens "
    "and new mines, but the rules and the spaceships are the same."
)

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


class TwoStepExp0:
    """Kool, Cushman & Gershman (2016), PLoS Comput Biol, Experiment 1: the
    Daw two-step task (original structure).

    Design (Methods > The Daw two-step task; Experimental methods,
    Materials and procedure, p. 20): 25 self-paced practice trials then 125
    timed (2 s) test trials. Each trial: a stage-1 choice between two
    spaceships (free, A/B) leads to one of two second-stage states via a
    common (70%) / rare (30%) transition; a stage-2 choice between two aliens
    (free, A/B) pays binary reward (0/1). Reward probabilities per alien
    follow an independent Gaussian random walk (mean 0, sigma 0.025) with
    reflecting boundaries at 0.25 and 0.75, freshly initialized at the start
    of each phase from complementary pairs {0.25,0.75} or {0.4,0.6}.

    ASSUMPTION: reward probabilities are re-initialized at the practice/test
    boundary (the shipped data jump 0.4->0.25 for subject_1's ps1a1 there,
    and each phase's first trial shows fresh complementary pairs).
    ASSUMPTION: no stage-1 or stage-2 timeouts are simulated (a text
    simulator cannot produce reaction times); every trial completes, valid=1.
    ASSUMPTION: the letter->identity mapping is regenerated exactly as
    build_jsonl.py does (md5-seeded from the participant id; one A/B map per
    participant shared by spaceships and aliens), so the round trip through
    build_jsonl.py is byte-identical.

    The DataFrame matches exp0.csv minus the columns a text simulator cannot
    produce (rt, rt_1, rt_2, stim_*, choice*, trial_number, time_elapsed,
    age, gender, score_final, time_total_ms, ps*).
    """

    def __init__(self):
        self.name = "kool_2016_when_exp0"
        self.num_practice = 25
        self.num_test = 125
        self.common_p = 0.70
        self.walk_sigma = 0.025
        self.bounds = (0.25, 0.75)
        self.init_pairs = [(0.25, 0.75), (0.4, 0.6)]

    def _fresh_ps(self, rng):
        ps = {}
        for st in (1, 2):
            pair = list(rng.choice(self.init_pairs))
            if rng.random() < 0.5:
                pair.reverse()
            ps[f"s{st}a1"], ps[f"s{st}a2"] = pair
        return ps

    def _step_ps(self, p, rng):
        p += rng.gauss(0.0, self.walk_sigma)
        if p < self.bounds[0]:
            p = 2 * self.bounds[0] - p
        if p > self.bounds[1]:
            p = 2 * self.bounds[1] - p
        return p

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for sim in tqdm(range(num_simulations)):
            pid = f"sim{sim}"
            rng = _rng(f"kool2016-exp0-{pid}")
            lm = _letter_map(rng)
            letters = (lm, lm)  # one A/B map per participant: (spaceships, aliens)
            s1_opts = list(letters[0].values())
            s2_opts = list(letters[1].values())

            ps = self._fresh_ps(rng)
            prompt = INSTRUCTIONS
            score = 0
            for block in range(self.num_practice + self.num_test):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                phase = "practice" if block < self.num_practice else "test"
                if block == self.num_practice:
                    ps = self._fresh_ps(rng)
                    prompt += f"\n{BOUNDARY}"

                prompt += "\nYou see two spaceships. You press [HUMAN_RESPONSE]"
                s1l = agent(prompt, choice_options=s1_opts)
                s1 = next(k for k, v in letters[0].items() if v == s1l)
                prompt += f"{s1l}[/HUMAN_RESPONSE]."

                common = 1 if rng.random() < self.common_p else 0
                s2 = s1 + 1 if common == 1 else 2 - s1
                planet = PLANET[(phase == "practice", s2)]
                prompt += (f" You travel to the {planet} planet. On the planet you see "
                           "two aliens. You press [HUMAN_RESPONSE]")
                s2l = agent(prompt, choice_options=s2_opts)
                s2c = next(k for k, v in letters[1].items() if v == s2l)
                prompt += f"{s2l}[/HUMAN_RESPONSE]."

                win = 1 if rng.random() < ps[f"s{s2}a{s2c + 1}"] else 0
                prompt += (" You find a piece of space treasure!" if win
                           else " You find no space treasure.")
                score += win

                rows.append({
                    "participant_id": pid, "block": block, "trial": 2 * block,
                    "phase": phase, "stage": "stage1", "response": float(s1),
                    "reward": np.nan, "state": 0.0, "valid": 1, "state2": s2,
                    "common": common, "score": score,
                })
                rows.append({
                    "participant_id": pid, "block": block, "trial": 2 * block + 1,
                    "phase": phase, "stage": "stage2", "response": float(s2c),
                    "reward": float(win), "state": float(s2 - 1), "valid": 1,
                    "state2": s2, "common": common, "score": score,
                })

                for k in ps:
                    ps[k] = self._step_ps(ps[k], rng)
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "block", "trial", "phase", "stage", "response",
            "reward", "state", "valid", "state2", "common", "score",
        ])
        return df, prompts


def _random_agent(prompt, choice_options, choices=None):
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

    task = TwoStepExp0()
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