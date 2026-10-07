# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 (Study 2) of ``Hugging-Brain/olschewski_2024_frequent``,
format-identical to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
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
    """30 representative ints of a skewed continuous distribution (skew +1 or -1)."""
    g = np.sort(np.random.gamma(0.5, 1.0, 30))
    if skew == "left":
        g = -g[::-1]
    g = (g - g.mean()) / g.std() * sd + mean
    return np.round(g).astype(int).tolist()


def _yoked(left, right, k):
    """Reorder two independent 30-value lists so 'left > right' holds ~k/30 times."""
    L = sorted(left)
    R = np.roll(np.array(sorted(right)), int(30 - k))
    return L, R.tolist()


class BrokerGameStudy2:
    """Study 2 (exp1) of Olschewski, Spektor & Le Mens (2024), PNAS 121, e2317751121.

    Design (Materials and Methods, Study 2): 18 decisions -- 2 expected-value
    sensitivity ("catch") trials plus 8 continuous-skew and 8 discrete-skew trials.
    All options within a trial share mean 350/400/450/500 and the same SD
    (33.69 continuous, 15.15 discrete); continuous options are 30 equally spaced
    quantiles of a distribution with standardized skewness +/-1.72, discrete options
    have three unique outcomes (each 10 times) with skewness +/-0.56. Four trials
    yoke each pair so the left-skewed option wins 20/30 comparisons ("consleftwin" /
    "disleftwin"), four so the right-skewed wins ("consrightwin" / "disrightwin").
    side_right = 1 when the right option is the right-skewed one.

    ASSUMPTION (continuous yoking): the quantile lists are generated independently
    and paired via a cyclic rotation of the sorted right list, giving approx. 20/30
    wins in the intended direction (exact yoking procedure not recoverable).

    ASSUMPTION (catch): the two superior/inferior catch pairs use three-outcome
    discrete options with a 48-point expected-value gap and +/-28 offsets.

    The DataFrame matches exp1.csv (participant_id, trial, response, condition,
    samples_left, samples_right, side_right, valid).
    """

    def __init__(self):
        self.name = "olschewski_2024_frequent_exp1"
        self.n_decisions = 18
        self.n_pairs = 30
        self.means = [350, 400, 450, 500]
        self.sd_con = 33.69
        self.sd_dis = 15.15

    @staticmethod
    def _three_outcomes(mean, skew):
        if skew == "left":
            return [round(mean - 26), round(mean + 8), round(mean + 18)]
        return [round(mean - 18), round(mean - 8), round(mean + 26)]

    def _discrete_sequences(self, mean, right_skewed):
        # returns (left_vals, right_vals) as 30-lists; right_skewed tells which
        # physical side hosts the right-skewed distribution.
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
        sup = [sup_mean - 28] * 10 + [sup_mean] * 10 + [sup_mean + 28] * 10
        inf = [inf_mean - 28] * 10 + [inf_mean] * 10 + [inf_mean + 28] * 10
        sup = [float(x) for x in sup]
        inf = [float(x) for x in inf]
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
            for m, winner in zip(con_means, ["left", "left", "right", "right"] * 2):
                plan.append(("con", m, winner))
            for m, winner in zip(dis_means, ["left", "left", "right", "right"] * 2):
                plan.append(("dis", m, winner))
            plan.append(("catch", 0, None))
            plan.append(("catch", 1, None))
            np.random.shuffle(plan)
            for trial, (cond, m, winner) in enumerate(plan):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                if cond == "catch":
                    sl, sr = self._catch_sequences(m)
                    slm = float(np.mean(sl))
                    srm = float(np.mean(sr))
                    side_right = int(srm < slm)  # right is the inferior/losing stock
                else:
                    right_skewed = bool(np.random.rand() < 0.5)
                    side_right = int(right_skewed)
                    if cond == "dis":
                        lv, rv = self._discrete_sequences(m, right_skewed)
                    else:
                        lv = _skewed_quantiles(m, self.sd_con, "left" if right_skewed else "right")
                        rv = _skewed_quantiles(m, self.sd_con, "right" if right_skewed else "left")
                    k = 20 if winner == "left" else 10  # left-skewed option wins 20/30
                    sl, sr = _yoked(lv, rv, k)
                    if cond == "con":
                        cond = f"cons{'right' if winner=='right' else 'left'}win"
                    else:
                        cond = f"dis{'right' if winner=='right' else 'left'}win"
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
    task = BrokerGameStudy2()
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