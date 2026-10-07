# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 of ``Hugging-Brain/binz_2022_heuristics`` (Exp 2,
known direction), format-identical to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import math
import random

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (INTRO and exp1's cover sentence).
INTRO = (
    "You are watching an alien sports competition on an unknown planet. "
    "Each round of the competition pits two aliens, Alien 1 and Alien 2, "
    "against each other. The two aliens are described by numerical attributes. "
    "Your task is to predict, for each round, which alien is more likely to win. "
    "After you decide, you are told the correct choice."
)
COVER_EXTRA = (
    "For every attribute, a higher value makes it more likely that an "
    "alien wins the competition."
)


def _diff_str(v):
    return f"{float(v):+.2f}"


def _letters(participant_id):
    """Per-participant letter mapping, identical to build_jsonl.py's policy
    (its Random(pid * 7919 + 12345) shuffle). Returns [letter_for_option0,
    letter_for_option1]."""
    rng = random.Random(int(participant_id) * 7919 + 12345)
    perm = ["A", "B"]
    rng.shuffle(perm)
    return perm


def _lkj_cholesky(d):
    """Sample the Cholesky factor of an LKJ(eta=2) correlation matrix,
    replicating torch.distributions.LKJCholesky's onion sampler in numpy."""
    w = np.zeros((d, d))
    w[0, 0] = 1.0
    marginal = 2.0 + 0.5 * (d - 2)
    for i in range(1, d):
        off = i - 1 if i > 1 else 0
        b1 = off + 0.5
        b0 = marginal - 0.5 * off
        y = np.random.beta(b1, b0)
        v = np.random.standard_normal(i)
        v /= np.sqrt((v * v).sum())
        w[i, :i] = np.sqrt(y) * v
        rem = 1.0 - (w[i, :i] ** 2).sum()
        w[i, i] = math.sqrt(max(rem, 1e-9))
    return w


class KnownDirectionPairedComparison:
    """Cued two-alternative forced-choice task, Experiment 2 (known direction)
    of Binz, Gershman, Schulz & Endres (2022), "Heuristics from bounded
    meta-learned inference", Psychological Review, 129(5), 1042-1077.

    Design (pp. 42-44, "Experiment 2: Known Direction"): identical to
    Experiment 1, except participants are told that higher feature values
    always make it more likely that an alien wins. Per environments.py, the
    direction manipulation uses feature weights w = |N(0, I)| (all positive);
    the winner is a Bernoulli draw with p = 0.5*erfc(-(w.T (xa-xb)) / (2
    sigma)) and the stored target is then flipped to 1 - C as in the reference
    implementation ("hack to fix an earlier bug"). Every participant sees the
    same 30 tasks in a randomized order.

    ASSUMPTION: sigma = 0.1 and the target flip come verbatim from
    environments.py; the paper only describes sigma as making an ideal
    observer ~85% correct at the tenth trial (p. 29).
    ASSUMPTION: the task pool is drawn fresh per ``simulate`` call, shared
    across simulated participants, with each participant receiving a fresh
    random task order (Procedure, p. 42).

    The DataFrame matches exp1.csv minus ``time`` (an RT-based column a text
    simulator cannot produce).
    """

    def __init__(self):
        self.name = "binz_2022_heuristics_exp1"
        self.num_tasks = 30
        self.trials_per_task = 10
        self.n_features = 4
        self.sigma = 0.1

    def _sample_task(self):
        w = np.abs(np.random.standard_normal(self.n_features))
        L = _lkj_cholesky(self.n_features)
        xs, ys = [], []
        for _ in range(self.trials_per_task):
            xa = L @ np.random.standard_normal(self.n_features)
            xb = L @ np.random.standard_normal(self.n_features)
            x = np.round(xa - xb, 2)
            p = 0.5 * math.erfc(-float(w @ x) / (2.0 * self.sigma))
            c = 1 if np.random.random() < p else 0
            y = 1 - c
            xs.append(x)
            ys.append(y)
        return np.array(xs), np.array(ys)

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        task_pool = [self._sample_task() for _ in range(self.num_tasks)]
        for participant in tqdm(range(num_simulations)):
            perm = np.random.permutation(self.num_tasks)
            ltrs = _letters(participant)
            prompt = INTRO
            prompt += (
                f"\nOn each trial you see the difference between the two aliens' "
                f"attributes, listed as Alien 1 minus Alien 2. {COVER_EXTRA} "
                f"To choose, press {ltrs[0]} for Alien 1 or {ltrs[1]} for Alien 2."
            )
            for pos in range(self.num_tasks):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                xs, ys = task_pool[int(perm[pos])]
                for trial in range(self.trials_per_task):
                    x = xs[trial]
                    target = int(ys[trial])
                    diffs = ", ".join(_diff_str(v) for v in x)
                    prompt += (
                        f"\nRound {pos + 1}: attribute differences "
                        f"(Alien 1 minus Alien 2): {diffs}. You press "
                        f"[HUMAN_RESPONSE]"
                    )
                    letter = agent(prompt, choice_options=[ltrs[0], ltrs[1]])
                    response = 0 if letter == ltrs[0] else 1
                    winner = "Alien 1" if target == 0 else "Alien 2"
                    outcome = "correct" if response == target else "incorrect"
                    prompt += (
                        f"{letter}[/HUMAN_RESPONSE]. The correct choice was "
                        f"{winner}. Your choice was {outcome}."
                    )
                    rows.append({
                        "participant_id": participant, "task_id": pos,
                        "trial": trial, "response": response, "target": target,
                        "correct": int(response == target),
                        "x0": float(x[0]), "x1": float(x[1]),
                        "x2": float(x[2]), "x3": float(x[3]),
                    })
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "task_id", "trial", "response", "target",
            "correct", "x0", "x1", "x2", "x3",
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
                        help="stop each participant at the task boundary at/past this many chars")
    parser.add_argument("--seed", type=int, default=None,
                        help="numpy random seed, for reproducible runs")
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    task = KnownDirectionPairedComparison()
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
        first = p.splitlines()[1]
        if len(first) > 220:
            first = first[:110] + " … " + first[-110:]
        print(f"participant {i} mapping line: {first}")
    print("=" * 78)
    print("prompt 0, head:")
    print(prompts[0][:700])
    print("...")
    print("prompt 0, tail:")
    print(prompts[0][-300:])


if __name__ == "__main__":
    main()