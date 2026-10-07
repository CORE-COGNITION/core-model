# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 (Multiple Price List) of ``Hugging-Brain/frey_2017_risk``,
format-identical to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp1). Responses are fixed L/R; no
# per-participant token randomization (the codebook codes choice 0 = left / 1 =
# right, and the data show choice 1 is always lottery A, so B is left, `L`, and
# A is right, `R`, as in the transcription).
INSTRUCTIONS = (
    "In this task you will see many pairs of lotteries. Each screen shows two "
    "lotteries, one on the left and one on the right, each with two possible payoffs "
    "and their chances. On every trial pick the lottery you prefer by choosing the "
    "left or the right option. Your choices may be paid out at the end. Press L to "
    "choose the left lottery, or R to choose the right lottery.\n")

# 66 price-list problems, in presentation order (dp ascending, then decision
# ascending), exactly the rows of the study's mplProblems.csv. B = left option
# (response 0), A = right option (response 1). Columns: (dp, decision, A_out1,
# A_out2, A_p1, B_out1, B_out2, B_p1).
MPL = [
    (1, 1, 2, 1.6, 0.1, 3.85, 0.1, 0.1),
    (1, 2, 2, 1.6, 0.2, 3.85, 0.1, 0.2),
    (1, 3, 2, 1.6, 0.3, 3.85, 0.1, 0.3),
    (1, 4, 2, 1.6, 0.4, 3.85, 0.1, 0.4),
    (1, 5, 2, 1.6, 0.5, 3.85, 0.1, 0.5),
    (1, 6, 2, 1.6, 0.6, 3.85, 0.1, 0.6),
    (1, 7, 2, 1.6, 0.7, 3.85, 0.1, 0.7),
    (1, 8, 2, 1.6, 0.8, 3.85, 0.1, 0.8),
    (1, 9, 2, 1.6, 0.9, 3.85, 0.1, 0.9),
    (1, 10, 2, 1.6, 1.0, 3.85, 0.1, 1.0),
    (2, 1, 60, -70, 0.5, 15, -5, 0.5),
    (2, 2, 60, -60, 0.5, 15, -5, 0.5),
    (2, 3, 60, -50, 0.5, 15, -5, 0.5),
    (2, 4, 60, -40, 0.5, 15, -5, 0.5),
    (2, 5, 60, -30, 0.5, 15, -5, 0.5),
    (2, 6, 60, -20, 0.5, 15, -5, 0.5),
    (2, 7, 60, -10, 0.5, 15, -5, 0.5),
    (3, 1, 30, -40, 0.5, 15, -5, 0.5),
    (3, 2, 30, -30, 0.5, 15, -5, 0.5),
    (3, 3, 30, -20, 0.5, 15, -5, 0.5),
    (3, 4, 30, -10, 0.5, 15, -5, 0.5),
    (3, 5, 30, -0.1, 0.5, 15, -5, 0.5),
    (4, 1, 50, -60, 0.5, 15, -5, 0.5),
    (4, 2, 60, -60, 0.5, 15, -5, 0.5),
    (4, 3, 70, -60, 0.5, 15, -5, 0.5),
    (4, 4, 80, -60, 0.5, 15, -5, 0.5),
    (4, 5, 90, -60, 0.5, 15, -5, 0.5),
    (4, 6, 100, -60, 0.5, 15, -5, 0.5),
    (4, 7, 110, -60, 0.5, 15, -5, 0.5),
    (4, 8, 120, -60, 0.5, 15, -5, 0.5),
    (4, 9, 130, -60, 0.5, 15, -5, 0.5),
    (4, 10, 140, -60, 0.5, 15, -5, 0.5),
    (4, 11, 150, -60, 0.5, 15, -5, 0.5),
    (4, 12, 160, -60, 0.5, 15, -5, 0.5),
    (4, 13, 170, -60, 0.5, 15, -5, 0.5),
    (4, 14, 180, -60, 0.5, 15, -5, 0.5),
    (4, 15, 190, -60, 0.5, 15, -5, 0.5),
    (4, 16, 200, -60, 0.5, 15, -5, 0.5),
    (5, 1, 20, -30, 0.5, 15, -5, 0.5),
    (5, 2, 30, -30, 0.5, 15, -5, 0.5),
    (5, 3, 40, -30, 0.5, 15, -5, 0.5),
    (5, 4, 50, -30, 0.5, 15, -5, 0.5),
    (5, 5, 60, -30, 0.5, 15, -5, 0.5),
    (5, 6, 70, -30, 0.5, 15, -5, 0.5),
    (5, 7, 80, -30, 0.5, 15, -5, 0.5),
    (5, 8, 90, -30, 0.5, 15, -5, 0.5),
    (5, 9, 100, -30, 0.5, 15, -5, 0.5),
    (5, 10, 110, -30, 0.5, 15, -5, 0.5),
    (5, 11, 120, -30, 0.5, 15, -5, 0.5),
    (6, 1, 60, -60, 0.46, 15, -5, 0.5),
    (6, 2, 60, -60, 0.54, 15, -5, 0.5),
    (6, 3, 60, -60, 0.58, 15, -5, 0.5),
    (6, 4, 60, -60, 0.63, 15, -5, 0.5),
    (6, 5, 60, -60, 0.67, 15, -5, 0.5),
    (6, 6, 60, -60, 0.71, 15, -5, 0.5),
    (6, 7, 60, -60, 0.75, 15, -5, 0.5),
    (6, 8, 60, -60, 0.79, 15, -5, 0.5),
    (6, 9, 60, -60, 0.83, 15, -5, 0.5),
    (6, 10, 60, -60, 0.87, 15, -5, 0.5),
    (6, 11, 60, -60, 0.91, 15, -5, 0.5),
    (7, 1, 30, -30, 0.42, 15, -5, 0.5),
    (7, 2, 30, -30, 0.58, 15, -5, 0.5),
    (7, 3, 30, -30, 0.67, 15, -5, 0.5),
    (7, 4, 30, -30, 0.75, 15, -5, 0.5),
    (7, 5, 30, -30, 0.83, 15, -5, 0.5),
    (7, 6, 30, -30, 0.91, 15, -5, 0.5),
]


def _fmt(x):
    x = float(x)
    return str(int(x)) if x == int(x) else f"{x:g}"


def _lottery(out1, out2, p1):
    p1 = float(p1)
    p2 = 100.0 - p1
    return (f"pays {_fmt(out1)} with a {p1:g}% chance and "
            f"{_fmt(out2)} with a {p2:g}% chance")


def _var2(o1, o2, p1):
    p1 = float(p1)
    p2 = 1.0 - p1
    mu = o1 * p1 + o2 * p2
    return p1 * (o1 - mu) ** 2 + p2 * (o2 - mu) ** 2


class MultiplePriceList:
    """Multiple price lists, exp1 of the Basel-Berlin Risk Study (Frey et al.
    2017, "Risk preference shares the psychometric structure of major
    psychological traits", Sci. Adv. 3, e1701381).

    Design (task 3 'Multiple price list', see mplProblems.csv): 66 fixed
    two-lottery problems spanning seven price lists (dp=1 the classic
    Holt-Laury list; dp=2..7 bespoke lists). Each problem has a fixed lottery on
    the left (B) and a fixed lottery on the right (A); the participant picks one.
    Stimuli are fully deterministic, so no generative draw is needed beyond the
    participant's L/R choice.

    The codebook codes ``choice`` as 0 = left / 1 = right, and in exp1.csv the
    source ``R`` column is a deterministic function of (dp, choice) for every
    participant, so the sides were fixed: choice 1 is always lottery A of
    mplProblems.csv and choice 0 is lottery B. Following the transcription
    (README "Text-format conversion"), B is the left option (response 0, ``L``)
    and A the right option (response 1, ``R``).

    The source ``R`` column ("risky = higher-variance choice", codebook) equals
    1 when the chosen lottery has strictly higher variance, except the single
    zero-variance dp1/dec10 tie, where R is 1 iff lottery B was chosen; this
    rule reproduces every R value in exp1.csv.
    """

    def __init__(self):
        self.name = "frey_2017_risk_exp1"
        self.problems = MPL

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            prompt = INSTRUCTIONS
            for trial, prob in enumerate(self.problems):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                dp, dec, ao1, ao2, ap1, bo1, bo2, bp1 = prob
                a = _lottery(ao1, ao2, ap1 * 100.0)
                b = _lottery(bo1, bo2, bp1 * 100.0)
                prompt += f"Left lottery {b}. Right lottery {a}. You press [HUMAN_RESPONSE]"
                letter = agent(prompt, choice_options=["L", "R"])
                response = 0.0 if letter == "L" else 1.0
                prompt += f"{letter}[/HUMAN_RESPONSE].\n"
                var_a = _var2(ao1, ao2, ap1)
                var_b = _var2(bo1, bo2, bp1)
                cv = var_b if response == 0.0 else var_a
                ov = var_a if response == 0.0 else var_b
                if cv > ov:
                    r = 1.0
                elif cv < ov:
                    r = 0.0
                else:
                    r = 1.0 if response == 0.0 else 0.0
                rows.append({
                    "participant_id": participant, "trial": trial,
                    "response": response, "dp": float(dp), "decision": float(dec),
                    "choice": response, "R": r,
                })
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "dp", "decision", "choice", "R",
        ])
        return df, prompts


def _random_agent(prompt, choice_options):
    return str(np.random.choice(choice_options))


def main():
    parser = argparse.ArgumentParser(
        description="Smoke-test this simulator with a uniform-random agent.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3, help="number of simulated participants (default: 3)")
    parser.add_argument("--max-chars", type=int, default=None, help="stop each participant at the block boundary at/past this many chars")
    parser.add_argument("--seed", type=int, default=None, help="numpy random seed, for reproducible runs")
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    task = MultiplePriceList()
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