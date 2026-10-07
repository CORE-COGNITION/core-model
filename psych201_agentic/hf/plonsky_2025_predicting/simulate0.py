# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/plonsky_2025_predicting``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
from math import comb

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp0), first paragraph.
INSTRUCTIONS = (
    "You will play a series of games. In each game you choose repeatedly "
    "between two lotteries, Option A and Option B, for 25 trials. For the "
    "first 5 trials of each game you get no feedback; from the 6th trial on, "
    "after each choice you see both the payoff you received and the payoff "
    "you would have received from the other option. In some games the "
    "probabilities of Option B's outcomes are not shown. On each trial, "
    "press A to choose Option A or B to choose Option B."
)

# Verbatim game structures from exp0.csv (one row per game_id). Each value:
# [Set, Ha, pHa, La, LotShapeA, LotNumA, Hb, pHb, Lb, LotShapeB, LotNumB, Amb, Corr]
GAMES = {
    211: [8, 96, 0.2, 3, "Symm", 5, 59, 0.5, -19, "-", 1, 0, 0],
    212: [8, -9, 1.0, -9, "-", 1, -6, 0.99, -36, "Symm", 9, 0, 0],
    213: [8, 1, 1.0, 1, "-", 1, 27, 0.05, 1, "-", 1, 1, 0],
    214: [8, 3, 1.0, 3, "-", 1, 74, 0.2, -20, "-", 1, 0, 0],
    215: [8, 32, 0.5, 14, "-", 1, 17, 0.99, 16, "Symm", 5, 0, 0],
    216: [8, 53, 0.05, -12, "R-skew", 7, -9, 1.0, -9, "-", 1, 0, 0],
    217: [8, -6, 1.0, -6, "Symm", 9, 93, 0.2, -35, "L-skew", 3, 0, 0],
    218: [8, 12, 1.0, 12, "-", 1, 83, 0.2, -13, "-", 1, 0, 0],
    219: [8, 14, 0.8, 13, "-", 1, 32, 0.05, 12, "Symm", 7, 0, -1],
    220: [8, -8, 1.0, -8, "-", 1, -8, 1.0, -8, "R-skew", 7, 0, 0],
    221: [8, 47, 0.4, -11, "-", 1, 21, 0.4, 1, "R-skew", 7, 0, 1],
    222: [8, 61, 0.2, -13, "L-skew", 4, 53, 0.4, -43, "L-skew", 3, 0, 0],
    223: [8, 3, 1.0, 3, "-", 1, 68, 0.01, -1, "-", 1, 0, 0],
    224: [8, 56, 0.5, 0, "-", 1, 41, 0.6, 5, "-", 1, 0, 0],
    225: [8, 8, 0.99, 5, "R-skew", 3, 8, 1.0, 8, "Symm", 5, 0, 0],
    226: [8, 23, 1.0, 23, "-", 1, 242, 0.1, 2, "-", 1, 0, 0],
    227: [8, 19, 1.0, 19, "-", 1, 26, 0.8, -19, "-", 1, 1, 0],
    228: [8, 0, 1.0, 0, "-", 1, 7, 0.05, -2, "Symm", 7, 0, 0],
    229: [8, 2, 1.0, 2, "-", 1, 0, 0.99, -3, "R-skew", 4, 1, 0],
    230: [8, 24, 0.75, 20, "-", 1, 17, 0.95, 7, "-", 1, 0, 0],
    231: [8, 22, 0.75, 10, "-", 1, 29, 0.75, -3, "-", 1, 0, 0],
    232: [8, 25, 0.4, 5, "Symm", 9, 46, 0.01, 8, "Symm", 7, 0, 0],
    233: [8, 18, 1.0, 18, "-", 1, 34, 0.1, 19, "-", 1, 0, 0],
    234: [8, -8, 1.0, -8, "-", 1, 47, 0.25, -17, "-", 1, 1, 0],
    235: [8, -8, 1.0, -8, "-", 1, -8, 0.6, -19, "L-skew", 4, 0, 0],
    236: [8, 15, 1.0, 15, "-", 1, 43, 0.01, 7, "Symm", 3, 0, 0],
    237: [8, 20, 0.6, 10, "L-skew", 2, 75, 0.5, -49, "-", 1, 1, 0],
    238: [8, 31, 0.05, 2, "Symm", 9, 28, 0.05, 14, "-", 1, 1, 0],
    239: [8, 34, 0.1, 30, "L-skew", 5, 35, 0.95, -1, "Symm", 9, 1, 0],
    240: [8, 19, 1.0, 19, "-", 1, 58, 0.01, 16, "L-skew", 2, 0, 0],
    241: [9, 17, 1.0, 17, "-", 1, 104, 0.4, -42, "R-skew", 7, 0, 0],
    242: [9, 23, 1.0, 23, "-", 1, 40, 0.25, 17, "-", 1, 0, 0],
    243: [9, 42, 0.4, 4, "R-skew", 3, 19, 1.0, 19, "R-skew", 4, 1, 0],
    244: [9, -8, 1.0, -8, "-", 1, -7, 0.9, -29, "-", 1, 0, 0],
    245: [9, 24, 1.0, 24, "-", 1, 71, 0.1, 16, "-", 1, 0, 0],
    246: [9, 8, 1.0, 8, "-", 1, 3, 0.99, -28, "-", 1, 0, 0],
    247: [9, 26, 1.0, 26, "-", 1, 22, 0.9, -9, "-", 1, 0, 0],
    248: [9, -10, 1.0, -10, "-", 1, -6, 0.25, -19, "Symm", 3, 0, 0],
    249: [9, 18, 0.75, 7, "-", 1, 16, 0.8, 9, "-", 1, 0, 0],
    250: [9, 19, 1.0, 19, "L-skew", 4, 78, 0.1, 13, "-", 1, 0, 0],
    251: [9, -5, 1.0, -5, "-", 1, 138, 0.2, -35, "-", 1, 0, 0],
    252: [9, 29, 1.0, 29, "-", 1, 79, 0.1, 17, "L-skew", 4, 0, 0],
    253: [9, 219, 0.05, -21, "Symm", 5, -4, 0.75, -15, "L-skew", 5, 0, 0],
    254: [9, 78, 0.2, 17, "Symm", 3, 214, 0.25, -34, "-", 1, 0, 0],
    255: [9, 0, 1.0, 0, "-", 1, -7, 0.8, -15, "-", 1, 0, 0],
    256: [9, 1, 1.0, 1, "-", 1, 74, 0.05, 4, "-", 1, 1, 0],
    257: [9, 34, 0.8, -21, "Symm", 3, 48, 0.4, 4, "-", 1, 0, 0],
    258: [9, 1, 1.0, 1, "-", 1, 13, 0.4, -3, "-", 1, 1, 0],
    259: [9, 3, 0.95, -8, "Symm", 5, 67, 0.2, -13, "Symm", 7, 1, 0],
    260: [9, 82, 0.2, -29, "-", 1, -7, 0.99, -10, "-", 1, 0, 0],
    261: [9, 28, 1.0, 28, "-", 1, 69, 0.4, 3, "Symm", 3, 0, 0],
    262: [9, 55, 0.05, 9, "L-skew", 3, 23, 0.8, -17, "Symm", 5, 0, 0],
    263: [9, 103, 0.01, 9, "-", 1, 29, 0.75, -44, "-", 1, 1, 0],
    264: [9, 26, 0.75, -9, "R-skew", 3, 82, 0.01, 13, "Symm", 9, 0, 0],
    265: [9, 30, 0.4, 13, "R-skew", 2, 146, 0.25, -25, "Symm", 5, 0, 1],
    266: [9, -2, 1.0, -2, "-", 1, 11, 0.5, -12, "-", 1, 0, 0],
    267: [9, -7, 1.0, -7, "-", 1, -6, 0.75, -19, "R-skew", 5, 0, 0],
    268: [9, 16, 1.0, 16, "-", 1, 23, 0.8, -15, "R-skew", 3, 0, 0],
    269: [9, -3, 1.0, -3, "-", 1, 149, 0.2, -34, "-", 1, 0, 0],
    270: [9, 62, 0.25, -18, "-", 1, -5, 0.9, -23, "-", 1, 0, 0],
}


# _num, _prob, _lottery_part and _lottery are verbatim from build_jsonl.py.
def _num(v):
    v = float(v)
    return str(int(v)) if v == int(v) else f"{v:g}"


def _prob(q):
    return f"{q:.6g}"


def _lottery_part(H, p, shape, num):
    """Outcomes of the lottery an option pays with probability p, as
    [(outcome, probability)] sorted by outcome (descending), probabilities
    already multiplied by p. CPC18 definitions (paper SI, pp. 5-6): the lottery
    has expected value H and LotNum outcomes; Symm = H + {-k/2..k/2}, k =
    LotNum-1, Binomial(k, 1/2); R-skew = H - LotNum - 1 + 2**i, L-skew =
    H + LotNum + 1 - 2**i, i = 1..LotNum, truncated geometric(1/2) with the last
    term's probability adjusted up; LotNum = 1 means the single outcome H."""
    H, p, num = float(H), float(p), int(num)
    if shape == "Symm" and num > 1:
        k = num - 1
        outs = [(H - k / 2 + i, p * comb(k, i) / 2 ** k) for i in range(num)]
    elif shape in ("R-skew", "L-skew") and num > 1:
        w = [0.5 ** i for i in range(1, num + 1)]
        w[-1] = w[-2]
        sign = 1 if shape == "R-skew" else -1
        outs = [(H + sign * (2 ** i - num - 1), p * w[i - 1]) for i in range(1, num + 1)]
    else:
        outs = [(H, p)]
    return sorted(outs, key=lambda t: -t[0])


def _lottery(H, p, L, shape, num, amb=0):
    """Render one option the way CPC18 described it on screen (paper Fig. 1):
    every outcome with its probability. An option that pays H with probability
    p and L otherwise reads "pays H with probability p, otherwise L"; a
    multi-outcome lottery lists all its outcomes. When Amb = 1 (Option B only)
    the participant saw the outcomes but not their probabilities."""
    p, L = float(p), float(L)
    lot = _lottery_part(H, p, shape, num)
    if int(amb) == 1:
        outs = sorted({o for o, _ in lot} | ({L} if p < 1 else set()), reverse=True)
        if len(outs) == 1:
            return f"pays {_num(outs[0])}"
        if len(outs) == 2:
            return f"pays {_num(outs[0])} or {_num(outs[1])}; the probabilities are not shown"
        return f"pays one of {', '.join(_num(o) for o in outs)}; the probabilities are not shown"
    if len(lot) == 1 and (p == 1 or lot[0][0] == L):
        return f"pays {_num(lot[0][0])}"
    text = ", ".join(f"{_num(o)} with probability {_prob(q)}" for o, q in lot)
    if p < 1:
        text += f", otherwise {_num(L)}"
    return f"pays {text}"


def _dist(H, p, L, shape, num):
    """Full outcome distribution of one option, [(outcome, prob)] ascending,
    used to draw payoffs."""
    d = {}
    for o, q in _lottery_part(H, p, shape, num):
        d[o] = d.get(o, 0.0) + q
    if float(p) < 1:
        d[float(L)] = d.get(float(L), 0.0) + 1 - float(p)
    return sorted(d.items())


def _quantile(dist, u):
    c = 0.0
    for o, q in dist:
        c += q
        if u < c:
            return int(o)
    return int(dist[-1][0])


class RepeatedLotteryChoice:
    """Repeated binary risky choice between two lotteries, Experiment (exp0)
    of Plonsky et al. (2025), "Predicting human decisions with behavioural
    theories and machine learning", Nature Human Behaviour 9(11), 2271-2284.

    Design (CPC18 prediction-competition Track 1): each participant is assigned
    a Set (8 or 9) of 30 of the 60 games (GameID 211-270); each game is a pair
    of lotteries, Option A (Ha/pHa/La anchors) and Option B (Hb/pHb/Lb), played
    over 25 trials. The 30 games appear in a per-participant random presentation
    order (Order 1-30; task_id = Order - 1). The first 5 trials of each game give no feedback; from
    trial 5 on the participant sees both the obtained and the forgone payoff.
    The 60 game structures are taken verbatim from exp0.csv (fixed per game_id).

    Payoffs are drawn from the full CPC18 outcome distributions implied by
    (H, pH, L, LotShape, LotNum) as defined in the paper's SI (pp. 5-6), the
    same distributions the transcripts describe. Corr is honoured with a shared
    "luck level": Corr = 1 draws both options at the same uniform quantile,
    Corr = -1 at opposite quantiles, Corr = 0 independently. Ambiguous Option B
    (Amb = 1) is described without its probabilities, as on the CPC18 screen.

    The DataFrame matches exp0.csv minus the columns a text simulator cannot
    produce (gender, button, site, age, rt).
    """

    def __init__(self):
        self.name = "plonsky_2025_predicting_exp0"
        self.num_trials = 25       # trials per game
        self.num_games = 30        # games per participant (per Set)
        self.games = GAMES

    def _draw(self, dist_a, dist_b, corr):
        u_a = np.random.rand()
        u_b = u_a if corr == 1 else (1 - u_a if corr == -1 else np.random.rand())
        return _quantile(dist_a, u_a), _quantile(dist_b, u_b)

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            # response tokens are fixed: A = Option A (response 0), B = B (1)
            set_ = np.random.choice([8, 9])
            games = sorted(g for g in self.games if self.games[g][0] == set_)
            order = np.random.permutation(games)  # presentation order 1..30
            prompt = INSTRUCTIONS
            for slot, game_id in enumerate(order):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                _, Ha, pHa, La, shA, nA, Hb, pHb, Lb, shB, nB, amb, corr = self.games[game_id]
                dist_a, dist_b = _dist(Ha, pHa, La, shA, nA), _dist(Hb, pHb, Lb, shB, nB)
                prompt += (f"\nGame (presentation {slot + 1}): Option A "
                           f"{_lottery(Ha, pHa, La, shA, nA)}. Option B "
                           f"{_lottery(Hb, pHb, Lb, shB, nB, amb)}.")
                for trial in range(self.num_trials):
                    Apay, Bpay = self._draw(dist_a, dist_b, corr)
                    block = trial // 5
                    prompt += f"\nTrial {trial}: You press [HUMAN_RESPONSE]"
                    letter = agent(prompt, choice_options=["A", "B"])
                    response = 0 if letter == "A" else 1
                    reward = Apay if response == 0 else Bpay
                    forgone = Bpay if response == 0 else Apay
                    if trial >= 5:
                        prompt += (f"{letter}[/HUMAN_RESPONSE]. You receive {reward}; you "
                                   f"would have received {forgone}.")
                    else:
                        prompt += f"{letter}[/HUMAN_RESPONSE]. (no feedback)"
                    rows.append({
                        "participant_id": participant, "trial": trial, "response": response,
                        "task_id": slot, "block": block, "Set": set_, "condition": "byprob",
                        "game_id": game_id, "Ha": Ha, "pHa": float(pHa), "La": La,
                        "LotShapeA": self.games[game_id][4], "LotNumA": self.games[game_id][5],
                        "Hb": Hb, "pHb": float(pHb), "Lb": Lb,
                        "LotShapeB": self.games[game_id][9], "LotNumB": self.games[game_id][10],
                        "Amb": self.games[game_id][11], "Corr": self.games[game_id][12],
                        "Order": slot + 1, "reward": reward, "forgone": forgone,
                        "Apay": Apay, "Bpay": Bpay,
                        "Feedback": 1 if trial >= 5 else 0,
                    })
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "task_id", "block", "Set", "condition",
            "game_id", "Ha", "pHa", "La", "LotShapeA", "LotNumA", "Hb", "pHb", "Lb",
            "LotShapeB", "LotNumB", "Amb", "Corr", "Order", "reward", "forgone",
            "Apay", "Bpay", "Feedback",
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

    task = RepeatedLotteryChoice()
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