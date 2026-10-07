# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 of ``Hugging-Brain/olschewski_2025_optimal``
(Study 2, choice session), format-identical to ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent.
"""
import argparse
import os

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp1).
INSTRUCTIONS = (
    "You take part in a risky-choice experiment. Earlier you rated pairs of lotteries on a "
    "sliding scale from -100 (preferring the left lottery) to +100 (preferring the right). Now "
    "you choose between pairs of lotteries. On each trial you see Lottery A and Lottery B. Press "
    "A to choose Lottery A, or press B to choose Lottery B. One trial is selected at the end and "
    "paid as a bonus in experimental pounds converted to sterling at 20 to 1."
)


class RiskyChoice:
    """Study 2 of Olschewski, Mullett & Stewart (2025), "Optimal allocation of time in risky
    choices under opportunity costs", Cognitive Psychology, 157, 101716.

    Design (4.1.1 Procedure and incentives): eight blocks whose conditions alternate in pairs of
    two between ``no_time_limit`` and ``time_limit``; the starting block type is randomized (data:
    116 start no_time_limit, 124 start time_limit).  ``build_jsonl.py`` emits a "New block: ..."
    line at the start of every block.  Each block has 20 analysed trials and every
    block contains 10 common-event plus 10 rare-event lottery pairs (confirmed by the data).  The
    time-limit blocks ran under an 80-second timer that ends the block when it reaches zero.

    Stimuli (4.1.2 Stimulus design): pairs of two-outcome lotteries, each outcome drawn 11-99 and
    each probability in the rare band (<=0.15 or >=0.85) or the common band (0.30-0.70, excluding
    0.50), with systematically varied EV- and SD-differences.  We resample each trial's exact
    lottery parameters (``player.o{1,2}``/``player.p{1,2}``) from the real exp1.csv rows grouped
    by condition and ``rare`` so the narrated lottery lines read exactly like real ones.

    ASSUMPTION: exp1.csv stores 20 rows per block even though time-limit blocks had blocktotal=40
    in the source; we mirror the CSV (20 trials/block) and set ``player.blocktotal`` to 20;
    build_jsonl.py does not use this column.

    ASSUMPTION: end-of-session payment is the drawn outcome of one played-out lottery: we select
    one trial, play its chosen lottery (or a uniform-random one when no choice was made), and
    record that outcome as ``reward`` on the participant's final row, matching the shipped data
    where only the last row has a non-zero reward.

    ASSUMPTION: timeouts are not modelled - the uniform test agent always answers, so ``valid``
    is always 1 and every trial line is a free marked choice.

    The DataFrame mirrors exp1.csv minus ``rt``/``rtsec``/``lagchoice``/``rtrank``/``rtbins``, raw
    page timestamps / oTree bookkeeping and rating-session columns a text simulator cannot produce.
    """

    def __init__(self):
        self.name = "olschewski_2025_optimal_exp1"
        self.num_blocks = 8
        self.trials_per_block = 20
        self._pool = None

    def _load_pool(self):
        if self._pool is not None:
            return self._pool
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exp1.csv")
        df = pd.read_csv(path, usecols=[
            "condition", "rare",
            "player.oa1", "player.oa2", "player.pa1", "player.pa2",
            "player.ob1", "player.ob2", "player.pb1", "player.pb2",
            "eva", "evb", "evd", "absevd", "sda", "sdb", "sdd",
        ])
        pool = {}
        for (cond, rare), g in df.groupby(["condition", "rare"]):
            pool[(cond, int(rare))] = g.to_dict("records")
        self._pool = pool
        return pool

    def _draw(self, pool, cond, rare):
        g = pool.get((cond, int(rare)))
        return dict(g[np.random.randint(len(g))]) if g is not None else None

    def simulate(self, agent, num_simulations, max_chars=None):
        pool = self._load_pool()
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            start_free = bool(np.random.rand() < 0.5)
            prompt = INSTRUCTIONS
            trial = 0
            for block in range(self.num_blocks):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                free = ((block % 4) < 2) == start_free
                cond = "no_time_limit" if free else "time_limit"
                # one header per block, as in build_jsonl.py
                if free:
                    prompt += "\nNew block: no time limit."
                else:
                    prompt += (
                        "\nNew block: an 80-second timer counts down and the block ends "
                        "when it reaches zero."
                    )
                # each block: 10 rare + 10 common pairs, shuffled
                rares = [1] * (self.trials_per_block // 2) + [0] * (self.trials_per_block // 2)
                np.random.shuffle(rares)
                for block_trial, rare in enumerate(rares):
                    rec = self._draw(pool, cond, rare)
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
                        "reward": 0, "condition": cond, "valid": 1, "rare": int(rare),
                        "player.oa1": int(rec["player.oa1"]),
                        "player.oa2": int(rec["player.oa2"]),
                        "player.pa1": int(rec["player.pa1"]),
                        "player.pa2": int(rec["player.pa2"]),
                        "player.ob1": int(rec["player.ob1"]),
                        "player.ob2": int(rec["player.ob2"]),
                        "player.pb1": int(rec["player.pb1"]),
                        "player.pb2": int(rec["player.pb2"]),
                        "player.blockround": block_trial + 1,
                        "player.blocktotal": 40 if not free else self.trials_per_block,
                        "eva": rec["eva"], "evb": rec["evb"], "evd": rec["evd"],
                        "absevd": rec["absevd"], "sda": rec["sda"], "sdb": rec["sdb"],
                        "sdd": rec["sdd"],
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
            "participant_id", "trial", "response", "block", "reward", "condition", "valid", "rare",
            "player.oa1", "player.oa2", "player.pa1", "player.pa2",
            "player.ob1", "player.ob2", "player.pb1", "player.pb2",
            "player.blockround", "player.blocktotal",
            "eva", "evb", "evd", "absevd", "sda", "sdb", "sdd",
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