# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 (Study 1) of ``Hugging-Brain/olschewski_2024_frequent``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import hashlib
import json

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_broker), with the letter slots kept.
INSTRUCTIONS = (
    "You play the role of a stock broker. On each decision you see two stocks side "
    "by side: the LEFT stock and the RIGHT stock. For each decision a history of the "
    "past 30 daily dividends of both stocks is shown, pair by pair (each pair shows "
    "one dividend from the left stock and, next to it, the same day's dividend from "
    "the right stock). After you have watched all 30 pairs, you decide which stock "
    "you want to draw a dividend from. "
    "Press {left} for the LEFT stock and {right} for the RIGHT stock. "
    "At the end one of your decisions is selected randomly and pays you that "
    "dividend as a bonus."
)


def _num(v):
    if v is None:
        return None
    f = float(v)
    return f"{f:g}"


def _broker_letters(pid):
    swap = hashlib.md5(str(pid).encode()).digest()[0] % 2 == 1
    return ("B", "A") if swap else ("A", "B")


def _pairs_str(sl, sr):
    return ", ".join(f"({_num(a)}, {_num(b)})" for a, b in zip(sl, sr))


def _jlist(arr):
    return json.dumps([float(x) for x in arr])


class BrokerGameStudy1:
    """Study 1 (exp0) of Olschewski, Spektor & Le Mens (2024), PNAS 121, e2317751121.

    Design (Materials and Methods, Study 1): 14 decisions per participant -- 2
    expected-value-sensitivity ("catch") trials plus 12 in three conditions of 4:
    a discrete two-outcome skewed pair ("disskewed"), a continuous skewed pair
    ("conskewed") and a symmetric Gaussian identical pair ("normal"). The four
    decisions within each condition are shifted versions with means 375/425/475/525
    (SD = 20). Each decision shows 30 dividend pairs of two stocks, then a choice.

    ASSUMPTION (continuous condition): the exact gamma -> linear-transform recipe
    (shape 0.5, scale 28.28, two >=3sigma extremes, target skew +2.06) is
    approximated by standardised gamma draws rescaled to the target mean/SD and
    rounded; the resulting values are plausible single draws from the same family.

    ASSUMPTION (normal yoking): the two Gaussian options present the same multiset of
    30 rounded values; the pairing is a cyclic rotation that gives the designated
    frequent winner the higher dividend in 20 of 30 pairs (10 when it is the loser).

    ASSUMPTION (catch): the two clearly-superior catch trials use two-outcome
    discrete options whose superior option has a ~50 point higher expected value.

    The DataFrame matches exp0.csv (participant_id, trial, response, condition,
    samples_left, samples_right, side_right, valid).
    """

    def __init__(self):
        self.name = "olschewski_2024_frequent_exp0"
        self.n_decisions = 14
        self.n_pairs = 30
        self.sd = 20.0
        self.means = [375, 425, 475, 525]

    def _normal_sequences(self, mean, side_right):
        v = np.sort(np.round(np.random.normal(mean, self.sd, self.n_pairs)))
        # rotation so left wins 's' of 30 comparisons; side_right=1 -> right is the
        # frequent loser -> left wins 20; side_right=0 -> left wins 10.
        s = 20 if side_right else 10
        right = np.roll(v, int(s))
        return v.tolist(), right.tolist()

    def _discrete_skew(self, mean, side_right):
        # left-skewed: frequent high (mean+9, 25/30) + rare low (mean-45, 5/30)
        # right-skewed: frequent low (mean-9, 25/30) + rare high (mean+45, 5/30)
        def opt(skew):
            common, rare = (mean + 9, mean - 45) if skew == "left" else (mean - 9, mean + 45)
            return [float(common)] * 25 + [float(rare)] * 5
        def side(skew):
            common, rare = (mean + 9, mean - 45) if skew == "left" else (mean - 9, mean + 45)
            arr = [float(common)] * 25 + [float(rare)] * 5
            np.random.shuffle(arr)
            return arr
        if side_right == 1:                       # right option is the losing/right-skewed
            left, right = side("left"), side("right")
        else:
            left, right = side("right"), side("left")
        return left, right

    def _continuous_sequence(self, mean, side_right):
        def draw(skew):
            g = np.random.gamma(0.5, 1.0, self.n_pairs)
            if skew == "left":
                g = -g
            g = (g - g.mean()) / g.std() * self.sd + mean
            return np.round(g).astype(int).tolist()
        if side_right == 1:
            return draw("left"), draw("right")
        return draw("right"), draw("left")

    def _catch_sequences(self, idx):
        # two clearly-superior catch trials, ~50 points higher EV on the superior side.
        base = 375 if idx == 0 else 350
        sup = [float(base - 20)] * 25 + [float(base + 20)] * 5
        inf = [float(base - 70)] * 25 + [float(base - 30)] * 5
        if np.random.rand() < 0.5:
            return sup, inf
        return inf, sup

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            pid = participant
            left, right = _broker_letters(pid)
            prompt = INSTRUCTIONS.format(left=left, right=right)
            # 4 means per experimental condition, shuffled
            normal_means = list(self.means); np.random.shuffle(normal_means)
            dis_means = list(self.means); np.random.shuffle(dis_means)
            con_means = list(self.means); np.random.shuffle(con_means)
            # build the 14 decisions and shuffle their order
            plan = []
            for m in normal_means:
                plan.append(("normal", m))
            for m in dis_means:
                plan.append(("disskewed", m))
            for m in con_means:
                plan.append(("conskewed", m))
            plan.append(("catch", 0))
            plan.append(("catch", 1))
            np.random.shuffle(plan)
            for trial, (cond, m) in enumerate(plan):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                side_right = int(np.random.rand() < 0.5)
                if cond == "normal":
                    sl, sr = self._normal_sequences(m, side_right)
                elif cond == "disskewed":
                    sl, sr = self._discrete_skew(m, side_right)
                elif cond == "conskewed":
                    sl, sr = self._continuous_sequence(m, side_right)
                else:
                    side_right = int(np.random.rand() < 0.5)
                    sl, sr = self._catch_sequences(m)
                # response: agent chooses a stock letter, coded 0 for LEFT, 1 for RIGHT
                prompt += (
                    f"\nDecision {trial}: the 30 dividend pairs (left, right) "
                    f"were: {_pairs_str(sl, sr)}. "
                    f"You press [HUMAN_RESPONSE]"
                )
                letter = agent(prompt, choice_options=[left, right])
                response = 0 if letter == left else 1
                prompt += f"{letter}[/HUMAN_RESPONSE]."
                rows.append({
                    "participant_id": pid, "trial": trial, "response": response,
                    "condition": cond, "samples_left": _jlist(sl),
                    "samples_right": _jlist(sr), "side_right": side_right, "valid": 1,
                })
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "condition",
            "samples_left", "samples_right", "side_right", "valid",
        ])
        return df, prompts


def _random_agent(prompt, choice_options):
    return str(np.random.choice(choice_options))


def main():
    parser = argparse.ArgumentParser(description="Smoke-test this simulator.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3)
    parser.add_argument("--max-chars", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()
    if args.seed is not None:
        np.random.seed(args.seed)
    task = BrokerGameStudy1()
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
        print(f"participant {i} first line: {first[:160]}")
    print("=" * 78)
    print("first prompt, head:")
    print(prompts[0][:700])
    print("...")
    print("first prompt, tail:")
    print(prompts[0][-300:])


if __name__ == "__main__":
    main()