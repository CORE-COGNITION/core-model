# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp2 (Study 3) of ``Hugging-Brain/olschewski_2024_frequent``,
format-identical to the repo's ``transcripts2.jsonl``.

``uv run simulate2.py -n 3`` smoke-tests with a uniform-random agent; or import
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


def _skewed_quantiles(mean, sd, skew):
    g = np.sort(np.random.gamma(0.5, 1.0, 30))
    if skew == "left":
        g = -g[::-1]
    g = (g - g.mean()) / g.std() * sd + mean
    return np.round(g).astype(int).tolist()


class BrokerGameStudy3:
    """Study 3 (exp2) of Olschewski, Spektor & Le Mens (2024), PNAS 121, e2317751121.

    Design (Materials and Methods, Study 3): 18 decisions -- 2 expected-value
    sensitivity ("catch") trials plus 8 continuous and 8 discrete skew trials with
    no frequent winner. Options within a trial share a mean of 350/400/450/500 and a
    common SD of ~33.5; continuous options are 30 equally spaced quantiles of a
    distribution with skew +/-1.72, discrete options have three unique outcomes
    (each 10 times) with skew +/-0.70. Unlike Studies 1-2 the sequences are NOT
    yoked: each option shows the higher dividend in about half of the 30 pairs.
    side_right = 1 when the right option is the right-skewed one.

    ASSUMPTION (continuous values): gamma quantiles mirror-generated for the two
    skew directions; the two tail extremes are not forced exactly as in the paper.

    ASSUMPTION (catch): the two superior/inferior catch pairs use three-outcome
    discrete options with a 48-point expected-value gap and +/-28 offsets.

    The DataFrame matches exp2.csv (participant_id, trial, response, condition,
    samples_left, samples_right, side_right, valid).
    """

    def __init__(self):
        self.name = "olschewski_2024_frequent_exp2"
        self.n_decisions = 18
        self.n_pairs = 30
        self.means = [350, 400, 450, 500]
        self.sd = 33.5

    @staticmethod
    def _three_outcomes(mean, skew):
        if skew == "left":
            return [round(mean - 47), round(mean + 21), round(mean + 26)]
        return [round(mean - 26), round(mean - 21), round(mean + 47)]

    def _discrete_sequences(self, mean, right_skewed):
        lo = self._three_outcomes(mean, "left")
        ro = self._three_outcomes(mean, "right")
        lv = [float(lo[0])] * 10 + [float(lo[1])] * 10 + [float(lo[2])] * 10
        rv = [float(ro[0])] * 10 + [float(ro[1])] * 10 + [float(ro[2])] * 10
        np.random.shuffle(lv)
        np.random.shuffle(rv)
        if right_skewed:
            return lv, rv
        return rv, lv

    def _catch_sequences(self, idx):
        sup_mean = 399 if idx == 0 else 351
        inf_mean = sup_mean - 48
        sup = [float(sup_mean - 28)] * 10 + [float(sup_mean)] * 10 + [float(sup_mean + 28)] * 10
        inf = [float(inf_mean - 28)] * 10 + [float(inf_mean)] * 10 + [float(inf_mean + 28)] * 10
        if np.random.rand() < 0.5:
            return sup, inf
        return inf, sup

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            pid = participant
            left, right = _broker_letters(pid)
            prompt = INSTRUCTIONS.format(left=left, right=right)
            plan = []
            con_means = list(self.means) * 2
            dis_means = list(self.means) * 2
            np.random.shuffle(con_means)
            np.random.shuffle(dis_means)
            for m in con_means:
                plan.append(("consequal", m))
            for m in dis_means:
                plan.append(("disequal", m))
            plan.append(("catch", 0))
            plan.append(("catch", 1))
            np.random.shuffle(plan)
            for trial, (cond, m) in enumerate(plan):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                if cond == "catch":
                    sl, sr = self._catch_sequences(m)
                    slm = float(np.mean(sl))
                    srm = float(np.mean(sr))
                    side_right = int(srm < slm)
                else:
                    right_skewed = bool(np.random.rand() < 0.5)
                    side_right = int(right_skewed)
                    if cond == "disequal":
                        lv, rv = self._discrete_sequences(m, right_skewed)
                    else:
                        lv = _skewed_quantiles(m, self.sd, "left" if right_skewed else "right")
                        rv = _skewed_quantiles(m, self.sd, "right" if right_skewed else "left")
                    # no frequent-winner yoking: each option wins about half
                    sl, sr = lv, rv
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
                    "samples_right": _jlist(sr),
                    "side_right": side_right, "valid": 1,
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
    task = BrokerGameStudy3()
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