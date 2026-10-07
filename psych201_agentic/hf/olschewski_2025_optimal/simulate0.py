# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/olschewski_2025_optimal``
(Study 1, choice session), format-identical to ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent.
"""
import argparse
import os

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp0).
INSTRUCTIONS = (
    "You take part in a risky-choice experiment. Earlier you rated 60 lotteries on a "
    "scale from 1 (least attractive) to 7 (most attractive). Now you choose between "
    "pairs of lotteries. On each trial you see Lottery A and Lottery B. Press A to "
    "choose Lottery A, or press B to choose Lottery B. At the end, one trial is "
    "selected and the chosen lottery played out, paying a bonus in experimental "
    "pounds converted to sterling at 20 to 1."
)
RATING_DIFFS = [1.0, 1.5, 2.5, 3.0]


class RiskyChoice:
    """Study 1 of Olschewski, Mullett & Stewart (2025), "Optimal allocation of time in
    risky choices under opportunity costs", Cognitive Psychology, 157, 101716.

    Design (Section 3.1): eight blocks per participant whose conditions alternate in
    pairs of two between ``known_utility`` and ``unknown_utility``, the starting block
    type randomized (data: 71 start known, 56 unknown). ``build_jsonl.py`` emits a
    "New block: ..." line at the start of every block; a known block's header states
    its rating difference. Known blocks: 20 trials, all pairs share one rating difference;
    each participant gets one known block per rating difference {1.0, 1.5, 2.5, 3.0}
    (3.1.2). Unknown blocks: 32 analysed trials per block (the CSV dropped the paper's
    filler pairs; we reproduce the 32 target trials, 8 per rating difference). A
    90-second red timer counts down during unknown blocks.

    Stimuli (3.1.2): two-outcome lotteries, outcomes drawn 1-99 with probabilities per
    the paper's construction. We resample each trial's exact lottery parameters
    (``player.o{1,2}``, ``player.p{1,2}``) from the real exp0.csv stimuli grouped by
    their ``player.ratingdiff`` so the narrated lines read exactly like real ones.

    ASSUMPTION: unknown-block rows in exp0.csv contain only the 32 target trials (the
    filler pairs are absent), so we generate 32-trial unknown blocks and set
    ``player.blocktotal`` accordingly; the field is not used by build_jsonl.py.

    ASSUMPTION: end-of-session payment is the drawn outcome of one played-out lottery:
    we pick one trial, play its chosen lottery (or a uniformly random one when no choice
    was made), and record that outcome as ``reward`` on the participant's final row,
    matching the shipped data where only the last row has a non-zero reward.

    ASSUMPTION: timeouts are not modelled - the uniform test agent always answers, so
    ``valid`` is always 1 and every trial line is a free marked choice.

    The DataFrame mirrors exp0.csv minus ``rt``/``rtsec``, raw page timestamps / oTree
    bookkeeping and rating-session columns a text simulator cannot produce.
    """

    def __init__(self):
        self.name = "olschewski_2025_optimal_exp0"
        self.num_blocks = 8
        self.known_trials = 20
        self.unknown_trials = 32
        self._pool = None

    def _load_pool(self):
        if self._pool is not None:
            return self._pool
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exp0.csv")
        df = pd.read_csv(path, usecols=[
            "player.ratingdiff", "player.stimuid", "player.gameidA", "player.gameidB",
            "player.oa1", "player.oa2", "player.pa1", "player.pa2",
            "player.ob1", "player.ob2", "player.pb1", "player.pb2",
            "eva", "evb", "evd", "sda", "sdb", "sdd",
        ])
        pool = {d: g.to_dict("records") for d, g in df.groupby("player.ratingdiff")}
        self._pool = pool
        return pool

    def _draw(self, pool, d):
        group = pool.get(d)
        return dict(group[np.random.randint(len(group))]) if group is not None else None

    def simulate(self, agent, num_simulations, max_chars=None):
        pool = self._load_pool()
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            start_known = bool(np.random.rand() < 0.5)
            blocked = RATING_DIFFS.copy()
            np.random.shuffle(blocked)
            next_diff = 0
            prompt = INSTRUCTIONS
            trial = 0
            for block in range(self.num_blocks):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                known = ((block % 4) < 2) == start_known
                condition = "known_utility" if known else "unknown_utility"
                # one header per block, as in build_jsonl.py
                if known:
                    d = blocked[next_diff]
                    next_diff += 1
                    prompt += (
                        "\nNew block: all pairs in this block have the same rating "
                        f"difference of {d} and there is no time limit."
                    )
                else:
                    prompt += (
                        "\nNew block: the pairs have varying rating differences, and a "
                        "90-second red timer counts down; the block ends when it reaches "
                        "zero."
                    )
                n = self.known_trials if known else self.unknown_trials
                ds = ([d] * n if known
                      else list(RATING_DIFFS) * (n // len(RATING_DIFFS)))
                if not known:
                    np.random.shuffle(ds)
                for block_trial in range(n):
                    d = ds[block_trial]
                    rec = self._draw(pool, d)
                    a = (f"{int(rec['player.oa1'])} at {int(rec['player.pa1'])}%, "
                         f"or {int(rec['player.oa2'])} at {int(rec['player.pa2'])}%")
                    b = (f"{int(rec['player.ob1'])} at {int(rec['player.pb1'])}%, "
                         f"or {int(rec['player.ob2'])} at {int(rec['player.pb2'])}%")
                    prompt += f"\nLottery A: {a}. Lottery B: {b}. You press [HUMAN_RESPONSE]"
                    letter = agent(prompt, choice_options=["A", "B"])
                    response = 0 if letter == "A" else 1
                    prompt += f"{letter}[/HUMAN_RESPONSE]."
                    rows.append({
                        "participant_id": participant, "trial": trial,
                        "response": float(response), "block": block,
                        "reward": 0, "condition": condition, "valid": 1,
                        "player.ratingdiff": d,
                        "player.stimuid": rec["player.stimuid"],
                        "player.gameidA": rec["player.gameidA"],
                        "player.gameidB": rec["player.gameidB"],
                        "player.oa1": int(rec["player.oa1"]),
                        "player.oa2": int(rec["player.oa2"]),
                        "player.pa1": int(rec["player.pa1"]),
                        "player.pa2": int(rec["player.pa2"]),
                        "player.ob1": int(rec["player.ob1"]),
                        "player.ob2": int(rec["player.ob2"]),
                        "player.pb1": int(rec["player.pb1"]),
                        "player.pb2": int(rec["player.pb2"]),
                        "player.blockround": block_trial + 1,
                        "player.blocktotal": 47 if not known else n,
                        "eva": rec["eva"], "evb": rec["evb"], "evd": rec["evd"],
                        "sda": rec["sda"], "sdb": rec["sdb"], "sdd": rec["sdd"],
                    })
                    trial += 1
            payout_row = rows[-1] if rows else None
            if not payout_row:
                reward = 0
            else:
                paid = payout_row
                chosen = (
                    (paid["player.oa1"], paid["player.pa1"], paid["player.oa2"], paid["player.pa2"])
                    if np.random.rand() < 0.5 else
                    (paid["player.ob1"], paid["player.pb1"], paid["player.ob2"], paid["player.pb2"])
                )
                o1, p1, o2, p2 = chosen
                reward = int(o1 if np.random.rand() * 100 < p1 else o2)
            if payout_row is not None:
                payout_row["reward"] = reward
            prompt += (
                "\nAt the end, one trial was selected for payment and the chosen lottery played "
                f"out. Your total bonus was {reward} experimental pounds."
            )
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "block", "reward", "condition", "valid",
            "player.ratingdiff", "player.stimuid", "player.gameidA", "player.gameidB",
            "player.oa1", "player.oa2", "player.pa1", "player.pa2",
            "player.ob1", "player.ob2", "player.pb1", "player.pb2",
            "player.blockround", "player.blocktotal", "eva", "evb", "evd", "sda", "sdb", "sdd",
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
                        help="stop each participant at the block boundary at/after this many chars")
    parser.add_argument("--seed", type=int, default=None, help="numpy random seed")
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    task = RiskyChoice()
    df, prompts = task.simulate(_random_agent, args.num_simulations, max_chars=args.max_chars)

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