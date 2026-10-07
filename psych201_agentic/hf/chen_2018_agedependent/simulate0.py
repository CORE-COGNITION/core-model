# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/chen_2018_agedependent`` (the
motor-gambling task), format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import hashlib

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp0), with the letter slots kept.
INSTRUCTIONS = (
    "Welcome to the motor gamble game. Your goal is to accumulate as many points as "
    "possible; you begin with 250 points. In each trial you see a path of 5 targets "
    "and a stake for that trial. Target difficulty runs from level 1 (largest, easiest "
    "target) to level 7 (smallest, hardest target). On a reward trial, skipping gives "
    "you +10 points; gambling means tapping all 5 targets from bottom to top within "
    "1.2 seconds to win a bigger prize (+20, +60, or +100 points), or 0 points if you "
    "fail. On a punishment trial, skipping costs you -10 points; gambling avoids the "
    "punishment (0 points) if you succeed but you lose a bigger amount (-20, -60, or "
    "-100) if you fail. If you gamble, tap the 5 targets in order, from bottom to top, "
    "as quickly and accurately as you can. On each trial press "
    "{skip_l} to skip the trial or {gamble_l} to take the gamble.")


def _letters(pid):
    """Skip/gamble key mapping, byte-identical to build_jsonl.py's policy."""
    h = int.from_bytes(hashlib.md5(str(pid).encode()).digest()[:2], "little")
    if h % 2 == 0:
        return "A", "B"
    return "B", "A"


def _pts(v):
    if pd.isna(v):
        return "You receive no points."
    v = int(round(float(v)))
    if v > 0:
        return f"You gain +{v} points."
    if v < 0:
        return f"You lose {-v} points."
    return "You gain 0 points."


class MotorGambleTask:
    """Motor-gambling task, Experiment (main app sample) of Chen et al. (2018),
    "Age-dependent Pavlovian biases influence motor decision-making", PLoS
    Comp Biol, 14(7), e1006304.

    Design (Methods, "Motor gambling task", p. 13): each participant plays 42
    trials = 6 value combinations (reward +20/+60/+100, punishment -20/-60/-100)
    x 7 target sizes. 7 blocks of 6 trials: blocks 1-3 present target sizes
    1-3, blocks 4-6 present sizes 4-6, and the final block the smallest size 7;
    within each block range the sizes and values are shuffled. Each trial shows
    the required action (target size + sine-curve path) and the participant
    either skips for a small stake (+10/-10) or gambles on successfully tapping
    the 5 targets within 1.2 s (reward: winscore vs 0; punishment: 0 vs
    losescore). Motor outcome is generated from per-level empirical success
    rates (Methods, "Materials and apparatus", p. 12).

    ASSUMPTION: per-target-size success probabilities and "did not start
    tapping within 7 s" probabilities are derived from exp0.csv (level 1 -> 7:
    P(success | started) = .735, .725, .679, .636, .552, .451, .363; P(no
    start) = .0095, .0147, .0243, .0409, .0678, .1033, .1518). The paper
    reports overall age-invariant motor performance and Fig 1G (success by
    target size) but not these trial-level constants.

    ASSUMPTION: sine-path parameters are drawn uniformly from the values seen
    in exp0.csv: amplitude over +-0.3..+-0.9 (step .1) and angle over
    integer 90..359 degrees (paper: angle randomly chosen between 0 and 360;
    data only contain 90-359).

    ASSUMPTION: participant covariates (age band, gender, education, device
    screen size, device type, location) are sampled from the empirical
    marginal distributions in exp0.csv.

    ASSUMPTION: the ``build_jsonl.py`` narration of a failed gamble always uses
    "You fail to tap all 5 targets in time and the ball sails past the coconut";
    the source codes "did not start in time" trials as ordinary failed gambles
    (perf=2), so they read identically in the transcript. This simulator
    reproduces that behaviour, so its text matches the repo transcripts exactly.

    The DataFrame matches exp0.csv minus the columns a text simulator cannot
    produce: ``rt``, ``time_stamps``, ``touch_x/y``, ``button_x/y``. ``valid``
    is always 1, mirroring exp0.csv (the source records a choice on every
    trial; "did not start in time" trials are failed gambles, outcome=2).
    """

    def __init__(self):
        self.name = "chen_2018_agedependent_exp0"
        self.start_points = 250
        self.num_blocks = 7
        self.block_size = 6
        self.radius_by_level = {1: 128, 2: 118, 3: 108, 4: 98, 5: 88, 6: 78, 7: 68}
        self.values = (
            {"RPscore": 20, "winscore": 20, "losescore": 0, "skipscore": 10},
            {"RPscore": 60, "winscore": 60, "losescore": 0, "skipscore": 10},
            {"RPscore": 100, "winscore": 100, "losescore": 0, "skipscore": 10},
            {"RPscore": -20, "winscore": 0, "losescore": -20, "skipscore": -10},
            {"RPscore": -60, "winscore": 0, "losescore": -60, "skipscore": -10},
            {"RPscore": -100, "winscore": 0, "losescore": -100, "skipscore": -10},
        )
        self.p_notstart = {1: 0.0095, 2: 0.0147, 3: 0.0243, 4: 0.0409,
                           5: 0.0678, 6: 0.1033, 7: 0.1518}
        self.p_success = {1: 0.735, 2: 0.725, 3: 0.679, 4: 0.636,
                          5: 0.552, 6: 0.451, 7: 0.363}
        self.amplitudes = [a / 10 for a in range(-9, 10) if a != 0 and abs(a) >= 3]
        self.age_groups = [
            (1, "18-24", 5889, (0.413, 0.587)),
            (2, "25-29", 4705, (0.395, 0.605)),
            (3, "30-39", 7333, (0.356, 0.644)),
            (4, "40-49", 4834, (0.380, 0.620)),
            (5, "50-59", 2452, (0.500, 0.500)),
            (6, "60_plus", 1319, (0.502, 0.498)),
        ]
        self.education = [0, 1, 2, 3]
        self.education_w = [2677, 6494, 11281, 6080]
        self.screen_raw = [4.0, 3.5, 9.7, 5.0, 4.8, 4.7, 4.3, 7.9, 7.0, 5.1, 3.7, 5.7]
        self.screen_w = [259.8, 146.4, 137.8, 94.5, 59.2, 53.6, 44.0, 36.4, 31.5, 20.6, 18.8, 16.4]
        self.device_types = [
            "iPhone5,2", "iPhone4,1", "iPhone6,2", "iPhone6,1", "iPhone3,1",
            "iPhone5,1", "samsung/jflte/jfltex", "samsung/m0/m0xx", "iPad2,1",
            "iPad3,4", "iPad2,5", "LGE/hammerhead/hamme", "iPad3,1", "iPad4,1",
        ]
        self.device_w = [2327, 2284, 1517, 1091, 963, 751, 673, 661, 618, 595, 551, 546, 499, 483]
        self.locations = [400, 2, 3, 0, 1, 900, 401, 4, 205, 5]
        self.location_w = [6381, 3340, 2121, 2006, 1560, 1028, 1017, 871, 489, 427]

    @staticmethod
    def _screen_bin(raw):
        if raw < 5.0:
            return 4
        if raw < 7.0:
            return 6
        if raw < 9.0:
            return 8
        return 10

    def _sample_covariates(self):
        age_n = np.array([a[2] for a in self.age_groups], dtype=float)
        age_code, age_label, gender = None, None, None
        g = np.random.choice(len(self.age_groups), p=age_n / age_n.sum())
        code, label, _, split = self.age_groups[g]
        age_code, age_label = code, label
        gender = np.random.choice(["f", "m"], p=list(split))
        education = int(np.random.choice(self.education, p=np.array(self.education_w) / sum(self.education_w)))
        raw = float(np.random.choice(self.screen_raw, p=np.array(self.screen_w) / sum(self.screen_w)))
        device = str(np.random.choice(self.device_types, p=np.array(self.device_w) / sum(self.device_w)))
        location = int(np.random.choice(self.locations, p=np.array(self.location_w) / sum(self.location_w)))
        return {
            "age": age_code, "age_group": age_label, "gender": gender,
            "education": education, "screen_size_raw": raw,
            "screen_size": self._screen_bin(raw), "device_type": device,
            "location": location,
        }

    def _build_trial_specs(self):
        specs = []
        for levels in ([1, 2, 3], [4, 5, 6]):
            block = [(lvl, vd) for lvl in levels for vd in self.values]
            np.random.shuffle(block)
            specs.extend(block)
        block7 = list(self.values)
        np.random.shuffle(block7)
        specs.extend((7, vd) for vd in block7)
        return specs

    def _motor_outcome(self, response, level, vd):
        if response == 0:
            return 0, 1, vd["skipscore"]
        if np.random.rand() < self.p_notstart[level]:
            return 2, 1, vd["losescore"]
        if np.random.rand() < self.p_success[level]:
            return 1, 1, vd["winscore"]
        return 2, 1, vd["losescore"]

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            pid = f"P{participant:05d}"
            skip_l, gamble_l = _letters(pid)
            prompt = INSTRUCTIONS.format(skip_l=skip_l, gamble_l=gamble_l)
            cov = self._sample_covariates()
            specs = self._build_trial_specs()
            total = self.start_points
            part_start = len(rows)
            for block in range(self.num_blocks):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                for k, (level, vd) in enumerate(specs[block * self.block_size:(block + 1) * self.block_size]):
                    trial = block * self.block_size + k
                    if vd["RPscore"] > 0:
                        stake = f"Reward trial: skip +10, gamble +{int(vd['winscore'])} or 0."
                    else:
                        stake = f"Punishment trial: skip -10, gamble 0 or {int(vd['losescore'])}."
                    diff = (f"Target difficulty level {int(level)} "
                            f"(radius {int(self.radius_by_level[level])} px).")
                    prompt += f"\n{stake} {diff} You press [HUMAN_RESPONSE]"
                    letter = agent(prompt, choice_options=[skip_l, gamble_l])
                    response = 0 if letter == skip_l else 1
                    outcome, valid, reward = self._motor_outcome(response, level, vd)
                    choice = "to skip the trial" if response == 0 else "to take the gamble"
                    if outcome == 0:
                        out = f"You skip the trial. {_pts(reward)}"
                    elif outcome == 1:
                        out = f"You tap all 5 targets in time and hit the coconut. {_pts(reward)}"
                    else:
                        out = (f"You fail to tap all 5 targets in time and the ball sails past "
                               f"the coconut. {_pts(reward)}")
                    prompt += f"{letter}[/HUMAN_RESPONSE] {choice}. {out}"
                    total += reward
                    rows.append({
                        "participant_id": pid, "trial": trial, "response": response,
                        "reward": reward, "age": cov["age"], "age_group": cov["age_group"],
                        "gender": cov["gender"], "education": cov["education"],
                        "level": level, "radius": self.radius_by_level[level],
                        "winscore": vd["winscore"], "losescore": vd["losescore"],
                        "skipscore": vd["skipscore"], "RPscore": vd["RPscore"],
                        "gamble": response, "outcome": outcome,
                        "amplitude": float(np.random.choice(self.amplitudes)),
                        "angle": int(np.random.randint(90, 360)),
                        "screen_size_raw": cov["screen_size_raw"],
                        "screen_size": cov["screen_size"], "point_final": total,
                        "device_type": cov["device_type"], "location": cov["location"],
                        "valid": valid,
                    })
            for rr in rows[part_start:]:
                rr["point_final"] = total
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "reward", "age", "age_group",
            "gender", "education", "level", "radius", "winscore", "losescore",
            "skipscore", "RPscore", "gamble", "outcome", "amplitude", "angle",
            "screen_size_raw", "screen_size", "point_final", "device_type",
            "location", "valid",
        ])
        df["reward"] = df["reward"].astype("float64")
        for c in ("winscore", "losescore", "skipscore", "RPscore", "amplitude", "screen_size_raw"):
            df[c] = df[c].astype("float64")
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

    task = MotorGambleTask()
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
