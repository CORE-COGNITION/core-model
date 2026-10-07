# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/binz_2022_heuristics`` (Exp 1,
known ranking), format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import math
import random

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (INTRO and exp0's cover sentence).
INTRO = (
    "You are watching an alien sports competition on an unknown planet. "
    "Each round of the competition pits two aliens, Alien 1 and Alien 2, "
    "against each other. The two aliens are described by numerical attributes. "
    "Your task is to predict, for each round, which alien is more likely to win. "
    "After you decide, you are told the correct choice."
)
COVER_EXTRA = (
    "The attributes are listed in order from the one that predicts the "
    "winner best to the one that predicts it worst; the first attribute is "
    "the most predictive and the last is the least predictive."
)

ROUND_FMT = (
    "Round {round_no}: attribute differences (Alien 1 minus Alien 2): "
    "{diffs}. You press [HUMAN_RESPONSE]{letter}[/HUMAN_RESPONSE]. "
    "The correct choice was {winner}. Your choice was {outcome}."
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


class KnownRankingPairedComparison:
    """Cued two-alternative forced-choice task, Experiment 1 (known ranking) of
    Binz, Gershman, Schulz & Endres (2022), "Heuristics from bounded
    meta-learned inference", Psychological Review, 129(5), 1042-1077.

    Design (pp. 36-38, "Experiment 1: Known Ranking"): each participant
    performs 30 paired-comparison tasks of 10 trials, framed as an alien
    sports competition. A task is generated per the model-section
    "Environments" (pp. 28-29) and the reference implementation
    ``environments.py`` of the paper's GitHub repo: feature weights
    w ~ N(0, I) sorted by |w| descending (the "known ranking" manipulation);
    each trial draws feature vectors xa, xb from a zero-mean normal with a
    per-task LKJ(eta=2) correlation matrix; the winner is a Bernoulli draw
    with p = 0.5*erfc(-(w.T (xa-xb)) / (2 sigma)); the participant sees the
    difference (Alien 1 minus Alien 2) and picks one. Every participant sees
    the same 30 tasks in a randomized order (Procedure, p. 36).

    ASSUMPTION: sigma = 0.1 is taken verbatim from environments.py's
    ``self.sigma = math.sqrt(0.01)``; the paper only says sigma is set so an
    ideal observer is ~85% correct on the tenth trial (p. 29) without
    reporting the number.
    ASSUMPTION: only the weights are permuted by |w|; the feature vectors are
    left in their drawn order, mirroring environments.py's ``get_batch``
    exactly (the weights are sorted, the inputs are not).
    ASSUMPTION: the LKJ(2) cholesky factor in numpy replicates
    torch LKJCholesky's onion sampler; this matches the observed marginal
    distribution of the published feature differences.
    ASSUMPTION: the 30-task pool is drawn fresh per ``simulate`` call and
    shared across simulated participants, and each participant receives a
    fresh random permutation of the tasks, matching the Procedure.

    The DataFrame matches exp0.csv minus ``time`` (an RT-based column a text
    simulator cannot produce).
    """

    def __init__(self):
        self.name = "binz_2022_heuristics_exp0"
        self.num_tasks = 30
        self.trials_per_task = 10
        self.n_features = 4
        self.sigma = 0.1

    def _sample_task(self):
        w_raw = np.random.standard_normal(self.n_features)
        w = w_raw[np.argsort(-np.abs(w_raw))]
        L = _lkj_cholesky(self.n_features)
        xs, ys = [], []
        for _ in range(self.trials_per_task):
            xa = L @ np.random.standard_normal(self.n_features)
            xb = L @ np.random.standard_normal(self.n_features)
            x = np.round(xa - xb, 2)
            p = 0.5 * math.erfc(-float(w @ x) / (2.0 * self.sigma))
            y = 1 if np.random.random() < p else 0
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
                f"To choose, press {ltrs[1]} for Alien 1 or {ltrs[0]} for Alien 2."
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
                    # source coding (environments.py, no direction flip):
                    # target=1 <=> option A ("Alien 1", the minuend) is better.
                    winner = "Alien 1" if target == 1 else "Alien 2"
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

    task = KnownRankingPairedComparison()
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