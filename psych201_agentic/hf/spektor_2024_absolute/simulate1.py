# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 of ``Hugging-Brain/spektor_2024_absolute``,
format-identical to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``."""
import argparse
import zlib

import numpy as np
import pandas as pd
from tqdm import tqdm


def _token_map(pid):
    """Per-participant response-token assignment, identical to build_jsonl.py."""
    if zlib.crc32(f"{pid}".encode("utf-8")) & 1:
        return "B", "A"
    return "A", "B"


def _fmt(a, b):
    """A lottery's two equiprobable outcomes as readable text (build_jsonl.py)."""
    a = int(a)
    b = int(b)
    if a >= 0 and b >= 0:
        return f"win {a} or {b}"
    if a < 0 and b < 0:
        return f"lose {-a} or {-b}"
    pos = max(a, b)
    neg = min(a, b)
    return f"win {pos} or lose {-neg}"


SESSION = 'You will complete two sessions about a week apart.'

SHOWUP = 'One decision from each of the two sessions is drawn at random afterwards and the lottery you chose is played out for real; a share of the resulting outcome is added to or subtracted from your show-up fee of GBP 1.50 per session, so your final payoff ranges from GBP 2.30 to GBP 3.70.'


def _instructions(x_tok, y_tok):
    return (
        "Welcome. In this study you will repeatedly choose between two lotteries, "
        "one labeled X and one labeled Y. Each lottery has two possible outcomes, "
        "each occurring with 50% probability. "
        "For example, 'X: win 10 or lose 6' means lottery X pays 10 or -6 with equal "
        f"chance. On each round, press {x_tok} to choose lottery X and {y_tok} to "
        f"choose lottery Y. {SESSION} {SHOWUP}"
    )
POOLS = {
    'loss_aversion': {
        '20;-20;32;-32': [12, 20, -20, 32, -32, 0.0, 0.0, 0.0, 28, 45],
        '12;-12;20;-20': [2, 12, -12, 20, -20, 0.0, 0.0, 0.0, 17, 28],
        '24;-24;28;-28': [13, 24, -24, 28, -28, 0.0, 0.0, 0.0, 34, 40],
        '48;-14;64;-30': [23, 48, -14, 64, -30, 17.0, 17.0, 0.0, 44, 66],
        '40;-18;52;-30': [34, 40, -18, 52, -30, 11.0, 11.0, 0.0, 41, 58],
        '44;-6;48;-10': [31, 44, -6, 48, -10, 19.0, 19.0, 0.0, 35, 41],
        '20;-6;36;-22': [33, 20, -6, 36, -22, 7.0, 7.0, 0.0, 18, 41],
        '52;-18;60;-26': [22, 52, -18, 60, -26, 17.0, 17.0, 0.0, 49, 61],
        '52;-6;56;-10': [38, 52, -6, 56, -10, 23.0, 23.0, 0.0, 41, 47],
        '40;-10;52;-22': [19, 40, -10, 52, -22, 15.0, 15.0, 0.0, 35, 52],
        '56;-6;64;-12': [49, 56, -6, 64, -12, 25.0, 26.0, -1.0, 44, 54],
        '16;-8;40;-32': [42, 16, -8, 40, -32, 4.0, 4.0, 0.0, 17, 51],
        '60;-26;64;-30': [24, 60, -26, 64, -30, 17.0, 17.0, 0.0, 61, 66],
        '16;-16;24;-24': [7, 16, -16, 24, -24, 0.0, 0.0, 0.0, 23, 34],
        '36;-18;40;-22': [40, 36, -18, 40, -22, 9.0, 9.0, 0.0, 38, 44],
        '48;-26;52;-30': [35, 48, -26, 52, -30, 11.0, 11.0, 0.0, 52, 58],
        '16;-16;28;-28': [8, 16, -16, 28, -28, 0.0, 0.0, 0.0, 23, 40],
        '12;-12;28;-28': [4, 12, -12, 28, -28, 0.0, 0.0, 0.0, 17, 40],
        '48;-18;60;-30': [18, 48, -18, 60, -30, 15.0, 15.0, 0.0, 47, 64],
        '48;-10;64;-26': [30, 48, -10, 64, -26, 19.0, 19.0, 0.0, 41, 64],
        '60;-10;64;-14': [27, 60, -10, 64, -14, 25.0, 25.0, 0.0, 49, 55],
        '16;-16;20;-20': [6, 16, -16, 20, -20, 0.0, 0.0, 0.0, 23, 28],
        '12;-12;16;-16': [1, 12, -12, 16, -16, 0.0, 0.0, 0.0, 17, 23],
        '36;-22;40;-26': [32, 36, -22, 40, -26, 7.0, 7.0, 0.0, 41, 47],
        '24;-8;44;-28': [41, 24, -8, 44, -28, 8.0, 8.0, 0.0, 23, 51],
        '52;-8;56;-6': [48, 52, -8, 56, -6, 22.0, 25.0, -3.0, 42, 44],
        '44;-8;60;-24': [36, 44, -8, 60, -24, 18.0, 18.0, 0.0, 37, 59],
        '52;-22;56;-26': [20, 52, -22, 56, -26, 15.0, 15.0, 0.0, 52, 58],
        '12;-14;16;-14': [45, 12, -14, 16, -14, -1.0, 1.0, -2.0, 18, 21],
        '44;-18;56;-30': [26, 44, -18, 56, -30, 13.0, 13.0, 0.0, 44, 61],
        '20;-20;24;-24': [10, 20, -20, 24, -24, 0.0, 0.0, 0.0, 28, 34],
        '24;-16;28;-20': [17, 24, -16, 28, -20, 4.0, 4.0, 0.0, 28, 34],
        '20;-12;32;-24': [16, 20, -12, 32, -24, 4.0, 4.0, 0.0, 23, 40],
        '12;-8;32;-28': [44, 12, -8, 32, -28, 2.0, 2.0, 0.0, 14, 42],
        '12;-12;32;-32': [5, 12, -12, 32, -32, 0.0, 0.0, 0.0, 17, 45],
        '60;-6;64;-10': [39, 60, -6, 64, -10, 27.0, 27.0, 0.0, 47, 52],
        '56;-14;60;-18': [29, 56, -14, 60, -18, 21.0, 21.0, 0.0, 49, 55],
        '44;-8;48;-8': [47, 44, -8, 48, -8, 18.0, 20.0, -2.0, 37, 40],
        '16;-16;32;-32': [9, 16, -16, 32, -32, 0.0, 0.0, 0.0, 23, 45],
        '28;-28;32;-32': [15, 28, -28, 32, -32, 0.0, 0.0, 0.0, 40, 45],
        '24;-24;32;-32': [14, 24, -24, 32, -32, 0.0, 0.0, 0.0, 34, 45],
        '36;-6;48;-18': [21, 36, -6, 48, -18, 15.0, 15.0, 0.0, 30, 47],
        '36;-10;40;-14': [25, 36, -10, 40, -14, 13.0, 13.0, 0.0, 33, 38],
        '12;-12;24;-24': [3, 12, -12, 24, -24, 0.0, 0.0, 0.0, 17, 34],
        '40;-16;44;-20': [37, 40, -16, 44, -20, 12.0, 12.0, 0.0, 40, 45],
        '28;-22;36;-30': [43, 28, -22, 36, -30, 3.0, 3.0, 0.0, 35, 47],
        '36;-26;44;-32': [46, 36, -26, 44, -32, 5.0, 6.0, -1.0, 44, 54],
        '56;-14;64;-22': [28, 56, -14, 64, -22, 21.0, 21.0, 0.0, 49, 61],
        '20;-20;28;-28': [11, 20, -20, 28, -28, 0.0, 0.0, 0.0, 28, 40],
    },
    'gain_seeking': {
        '24;-24;28;-28': [13, 24, -24, 28, -28, 0.0, 0.0, 0.0, 34, 40],
        '22;-52;26;-56': [20, 22, -52, 26, -56, -15.0, -15.0, 0.0, 52, 58],
        '12;-12;16;-16': [1, 12, -12, 16, -16, 0.0, 0.0, 0.0, 17, 23],
        '26;-48;30;-52': [35, 26, -48, 30, -52, -11.0, -11.0, 0.0, 52, 58],
        '18;-44;30;-56': [26, 18, -44, 30, -56, -13.0, -13.0, 0.0, 44, 61],
        '14;-56;18;-60': [29, 14, -56, 18, -60, -21.0, -21.0, 0.0, 49, 55],
        '10;-60;14;-64': [27, 10, -60, 14, -64, -25.0, -25.0, 0.0, 49, 55],
        '24;-24;32;-32': [14, 24, -24, 32, -32, 0.0, 0.0, 0.0, 34, 45],
        '16;-16;24;-24': [7, 16, -16, 24, -24, 0.0, 0.0, 0.0, 23, 34],
        '6;-60;10;-64': [39, 6, -60, 10, -64, -27.0, -27.0, 0.0, 47, 52],
        '26;-60;30;-64': [24, 26, -60, 30, -64, -17.0, -17.0, 0.0, 61, 66],
        '20;-20;24;-24': [10, 20, -20, 24, -24, 0.0, 0.0, 0.0, 28, 34],
        '8;-44;24;-60': [36, 8, -44, 24, -60, -18.0, -18.0, 0.0, 37, 59],
        '8;-24;28;-44': [41, 8, -24, 28, -44, -8.0, -8.0, 0.0, 23, 51],
        '16;-24;20;-28': [17, 16, -24, 20, -28, -4.0, -4.0, 0.0, 28, 34],
        '12;-12;20;-20': [2, 12, -12, 20, -20, 0.0, 0.0, 0.0, 17, 28],
        '12;-12;28;-28': [4, 12, -12, 28, -28, 0.0, 0.0, 0.0, 17, 40],
        '8;-52;6;-56': [48, 8, -52, 6, -56, -22.0, -25.0, 3.0, 42, 44],
        '12;-20;24;-32': [16, 12, -20, 24, -32, -4.0, -4.0, 0.0, 23, 40],
        '10;-36;14;-40': [25, 10, -36, 14, -40, -13.0, -13.0, 0.0, 33, 38],
        '26;-36;32;-44': [46, 26, -36, 32, -44, -5.0, -6.0, 1.0, 44, 54],
        '6;-52;10;-56': [38, 6, -52, 10, -56, -23.0, -23.0, 0.0, 41, 47],
        '16;-40;20;-44': [37, 16, -40, 20, -44, -12.0, -12.0, 0.0, 40, 45],
        '8;-44;8;-48': [47, 8, -44, 8, -48, -18.0, -20.0, 2.0, 37, 40],
        '18;-40;30;-52': [34, 18, -40, 30, -52, -11.0, -11.0, 0.0, 41, 58],
        '20;-20;28;-28': [11, 20, -20, 28, -28, 0.0, 0.0, 0.0, 28, 40],
        '14;-56;22;-64': [28, 14, -56, 22, -64, -21.0, -21.0, 0.0, 49, 61],
        '10;-40;22;-52': [19, 10, -40, 22, -52, -15.0, -15.0, 0.0, 35, 52],
        '8;-12;28;-32': [44, 8, -12, 28, -32, -2.0, -2.0, 0.0, 14, 42],
        '20;-20;32;-32': [12, 20, -20, 32, -32, 0.0, 0.0, 0.0, 28, 45],
        '18;-52;26;-60': [22, 18, -52, 26, -60, -17.0, -17.0, 0.0, 49, 61],
        '16;-16;28;-28': [8, 16, -16, 28, -28, 0.0, 0.0, 0.0, 23, 40],
        '16;-16;32;-32': [9, 16, -16, 32, -32, 0.0, 0.0, 0.0, 23, 45],
        '18;-48;30;-60': [18, 18, -48, 30, -60, -15.0, -15.0, 0.0, 47, 64],
        '8;-16;32;-40': [42, 8, -16, 32, -40, -4.0, -4.0, 0.0, 17, 51],
        '6;-36;18;-48': [21, 6, -36, 18, -48, -15.0, -15.0, 0.0, 30, 47],
        '16;-16;20;-20': [6, 16, -16, 20, -20, 0.0, 0.0, 0.0, 23, 28],
        '12;-12;24;-24': [3, 12, -12, 24, -24, 0.0, 0.0, 0.0, 17, 34],
        '6;-44;10;-48': [31, 6, -44, 10, -48, -19.0, -19.0, 0.0, 35, 41],
        '14;-12;14;-16': [45, 14, -12, 14, -16, 1.0, -1.0, 2.0, 18, 21],
        '18;-36;22;-40': [40, 18, -36, 22, -40, -9.0, -9.0, 0.0, 38, 44],
        '10;-48;26;-64': [30, 10, -48, 26, -64, -19.0, -19.0, 0.0, 41, 64],
        '22;-28;30;-36': [43, 22, -28, 30, -36, -3.0, -3.0, 0.0, 35, 47],
        '12;-12;32;-32': [5, 12, -12, 32, -32, 0.0, 0.0, 0.0, 17, 45],
        '6;-20;22;-36': [33, 6, -20, 22, -36, -7.0, -7.0, 0.0, 18, 41],
        '14;-48;30;-64': [23, 14, -48, 30, -64, -17.0, -17.0, 0.0, 44, 66],
        '6;-56;12;-64': [49, 6, -56, 12, -64, -25.0, -26.0, 1.0, 44, 54],
        '28;-28;32;-32': [15, 28, -28, 32, -32, 0.0, 0.0, 0.0, 40, 45],
        '22;-36;26;-40': [32, 22, -36, 26, -40, -7.0, -7.0, 0.0, 41, 47],
    },
}

class TwoSessionChoice:
    """Experiment 2 (LAC vs GSC across two sessions ~1 week apart) of Spektor,
    Kellen, Rieskamp, & Klauer (2024), JEP: General.

    Design (Method, Exp. 2): each participant completed 49 choice trials in each
    of two experimental sessions (task_id 0/1) about a week apart, one session
    in the loss-aversion condition (LAC) and one in the gain-seeking condition
    (GSC), counterbalanced (order = starting condition). The 49 lottery pairs
    per condition are taken verbatim from the repo's exp1.csv; within a session
    the 49 unique pairs appear once in a random order.

    The DataFrame matches exp1.csv minus the timing columns (rt, RT) and the
    display-side columns (Xloc, choice_loc, choice, session_no), which a text
    simulator cannot reproduce.
    """

    def __init__(self):
        self.name = "spektor_2024_absolute_exp1"
        self.trials_per_session = 49
        self.sessions = 2

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for pid in range(num_simulations):
            x_tok, y_tok = _token_map(pid)
            order = "goodfirst" if np.random.rand() < 0.5 else "badfirst"
            cond_of_session = (["loss_aversion", "gain_seeking"] if order == "goodfirst"
                               else ["gain_seeking", "loss_aversion"])
            firstbatch = 1 if np.random.rand() < 1 / 9.25 else 0
            lines = [_instructions(x_tok, y_tok)]
            for sess in range(self.sessions):
                if max_chars is not None and len("\n".join(lines)) >= max_chars:
                    break
                cond = cond_of_session[sess]
                pool = list(POOLS[cond].items())
                np.random.shuffle(pool)
                if sess == 0:
                    lines.append(f"Session {sess + 1} begins.")
                else:
                    lines.append(f"Session {sess + 1} begins (about a week later).")
                for pos, (tdef, (tid, x1, x2, y1, y2, xev, yev, evd, xvar, yvar)) in enumerate(pool):
                    prefix = (f"X: {_fmt(x1, x2)}. Y: {_fmt(y1, y2)}. "
                              "You press [HUMAN_RESPONSE]")
                    prompt = "\n".join(lines) + "\n" + prefix
                    letter = agent(prompt, choice_options=[x_tok, y_tok])
                    response = 0 if letter == x_tok else 1
                    riskier = (xvar > yvar) if response == 0 else (yvar > xvar)
                    lines.append(prefix + f"{letter}[/HUMAN_RESPONSE].")
                    rows.append({
                        "participant_id": pid, "trial": pos,
                        "response": response, "task_id": sess, "condition": cond,
                        "valid": 1, "trial_no": pos + 1, "trial_id": tid,
                        "Xout1": x1, "Xout2": x2, "Yout1": y1, "Yout2": y2,
                        "firstbatch": firstbatch, "XEV": xev, "YEV": yev,
                        "EVdiff": evd, "trial_definition": tdef, "Xvar": xvar,
                        "Yvar": yvar, "order": order,
                        "riskychoice": "risky" if riskier else "safe",
                    })
            prompts.append("\n".join(lines).strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "task_id", "condition", "valid",
            "trial_no", "trial_id", "Xout1", "Xout2", "Yout1", "Yout2",
            "firstbatch", "XEV", "YEV", "EVdiff", "trial_definition", "Xvar",
            "Yvar", "order", "riskychoice",
        ])
        return df, prompts


def _random_agent(prompt, choice_options):
    return str(np.random.choice(choice_options))


def main():
    parser = argparse.ArgumentParser(
        description="Smoke-test this simulator with a uniform-random agent.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3, help="number of simulated participants (default: 3)")
    parser.add_argument("--max-chars", type=int, default=None, help="stop each participant at the block/session boundary at/past this many chars")
    parser.add_argument("--seed", type=int, default=None, help="numpy random seed, for reproducible runs")
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    task = TwoSessionChoice()
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
