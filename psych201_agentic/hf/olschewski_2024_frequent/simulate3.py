# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp3 (Study 4) of ``Hugging-Brain/olschewski_2024_frequent``,
format-identical to the repo's ``transcripts3.jsonl``.

``uv run simulate3.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import hashlib
import json

import numpy as np
import pandas as pd
from tqdm import tqdm

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
    return f"{float(v):g}"


def _broker_letters(pid):
    swap = hashlib.md5(str(pid).encode()).digest()[0] % 2 == 1
    return ("B", "A") if swap else ("A", "B")


def _jlist(arr):
    return json.dumps([float(x) for x in arr])


def _pairs_str(sl, sr):
    return ", ".join(f"({_num(a)}, {_num(b)})" for a, b in zip(sl, sr))


def _reps(common, rare, n_common):
    """30 draws: n_common copies of 'common', the rest 'rare', shuffled in bins so
    the rare events are spread ~evenly across the sequence."""
    arr = [float(common)] * n_common + [float(rare)] * (30 - n_common)
    np.random.shuffle(arr)
    return arr


def _yoked_same(v, k):
    """Two orderings of the same multiset v such that 'left' wins k of 30."""
    vt = np.sort(np.array(v, dtype=float))
    return vt.tolist(), np.roll(vt, int(k)).tolist()


class BrokerGameStudy4:
    """Study 4 (exp3) of Olschewski, Spektor & Le Mens (2024), PNAS 121, e2317751121.

    Design (Supporting Information, Study 4): 17 decisions -- one EV-sensitivity
    ("catch") trial, four discrete-skew ("disskewed"), four continuous-skew
    ("conskewed"), four yoked-Gaussian ("normal") and two trials each where the
    discrete rare events are MORE frequent (10/30, "dismore") or LESS frequent
    (2/30, "disless"). All outcomes are single digits (1-9). The discrete skew
    pair is one option with left-skewed outcomes {1 (20%), 6 (80%)} against one
    with right-skewed outcomes {4 (80%), 9 (20%)} (means 5 and 5). side_right = 1
    when the right option is the frequent loser.

    ASSUMPTION (continuous/gaussian): the "normal" Gaussian outcomes are drawn as
    rounded clipped N(6, 1.4) values in a bin and yoked by a cyclic rotation so the
    frequent winner leads 20/30 pairings; the "conskewed" option uses the observed
    single-digit marginals (left: {1:2,2:1,3:1,4:4,5:8,6:11,7:3} and its mirror) as
    shape templates, shuffled within the sequence.

    ASSUMPTION (catch): the single catch trial uses the observed clearly-superior
    pair {6 (20), 9 (10)} vs {1 (10), 4 (20)} (expected values 7 vs 3).

    The DataFrame matches exp3.csv (participant_id, trial, response, condition,
    samples_left, samples_right, side_right, valid).
    """

    def __init__(self):
        self.name = "olschewski_2024_frequent_exp3"
        self.n_decisions = 17
        self.n_pairs = 30

    @staticmethod
    def _conskew_template(side):
        if side == "left":
            return [1, 1, 2, 3, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5,
                    6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7]
        return [9, 9, 8, 7, 6, 6, 6, 6, 5, 5, 5, 5, 5, 5, 5, 5,
                4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 3]

    @staticmethod
    def _count_reps(container, counts):
        arr = []
        for v, c in counts.items():
            arr += [float(v)] * c
        np.random.shuffle(arr)
        return arr

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            pid = participant
            left, right = _broker_letters(pid)
            prompt = INSTRUCTIONS.format(left=left, right=right)
            plan = (["disskewed"] * 4 + ["conskewed"] * 4 + ["normal"] * 4
                    + ["dismore"] * 2 + ["disless"] * 2 + ["catch"])
            np.random.shuffle(plan)
            for trial, cond in enumerate(plan):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                if cond == "disskewed":
                    lopt = _reps(1, 6, 24)         # left-skewed: {1(20%), 6(80%)}
                    ropt = _reps(4, 9, 24)         # right-skewed: {4(80%), 9(20%)}
                    side_right = int(np.random.rand() < 0.5)   # right may host the right-skewed (loser)
                    sl, sr = (lopt, ropt) if side_right else (ropt, lopt)
                elif cond == "conskewed":
                    lopt = list(self._conskew_template("left"))
                    ropt = list(self._conskew_template("right"))
                    np.random.shuffle(lopt); np.random.shuffle(ropt)
                    side_right = int(np.random.rand() < 0.5)
                    sl, sr = (lopt, ropt) if side_right else (ropt, lopt)
                elif cond == "normal":
                    v = np.clip(np.round(np.random.normal(6.0, 1.4, 30)), 3, 9).astype(int)
                    side_right = int(np.random.rand() < 0.5)
                    k = 20 if side_right else 10    # right is the loser -> left wins 20
                    sl, sr = _yoked_same(v, k)
                elif cond == "dismore":
                    lv = _reps(6, 1, 20)           # rare 10/30
                    rv = _reps(4, 9, 20)
                    sl, sr = lv, rv
                    lm, rm = float(np.mean(sl)), float(np.mean(sr))
                    side_right = int(rm < lm)      # right inferior
                elif cond == "disless":
                    lv = _reps(6, 1, 28)           # rare 2/30
                    rv = _reps(4, 9, 28)
                    sl, sr = rv, lv                # left-skewed (with fewer rares) on the left
                    lm, rm = float(np.mean(sl)), float(np.mean(sr))
                    side_right = int(rm < lm)
                else:                             # catch
                    lv = _reps(6, 9, 20)           # superior: mean 7
                    rv = _reps(4, 1, 20)           # inferior: mean 3
                    sl, sr = lv, rv
                    lm, rm = float(np.mean(sl)), float(np.mean(sr))
                    side_right = int(rm < lm)
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
    task = BrokerGameStudy4()
    df, prompts = task.simulate(_random_agent, args.num_simulations,
                                max_chars=args.max_chars)
    print(f"name: {task.name}")
    print(f"df shape: {df.shape}")
    print(df.dtypes.to_string())
    print(df.head(8).to_string())
    print(f"prompt lengths: {[len(p) for p in prompts]}")
    for i, p in enumerate(prompts):
        print(f"participant {i} first line: {p.splitlines()[0][:160]}")
    print("=" * 78)
    print("first prompt, tail:")
    print(prompts[0][-300:])


if __name__ == "__main__":
    main()