# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 (Study 1a) of ``Hugging-Brain/gunadi_2022_impact``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Conditions: 2(direction) x 2(frequency), flight-ticket scenario (paper Study 1a,
# "Study 1a", p. 15). Historical prices as in the paper and build_jsonl.py.
HIST = {
    "dec_single": [600, 600, 600, 600],
    "dec_multiple": [600, 550, 500, 450],
    "inc_single": [200, 200, 200, 200],
    "inc_multiple": [200, 250, 300, 350],
}
LABELS = ["4 weeks ago", "3 weeks ago", "2 weeks ago", "1 week ago"]
VARIABLE = {"dec_single": "DecrLow", "dec_multiple": "DecrHigh",
            "inc_single": "IncrLow", "inc_multiple": "IncrHigh"}
CONDITIONS = list(HIST.keys())


def _usd(v):
    f = float(v)
    return "$" + (str(int(f)) if f.is_integer() else f"{f:.2f}")


def _history(prices, labels):
    return ", ".join(f"{_usd(p)} ({l})" for p, l in zip(prices, labels))


class FlightDeferral:
    """Purchase-deferral task, Study 1a of Gunadi & Evangelidis (2022), "The
    impact of historical price information on purchase deferral", Journal of
    Marketing Research, 59(3), 623-640.

    Design (Study 1a, p. 15): a single between-subjects 2(direction) x
    2(frequency) decision about whether to buy a flight ticket now (response 0,
    token N) or wait/defer (response 1, token W). The price history is shown,
    the current price is always $400.

    ASSUMPTION: the condition is drawn uniformly at random per participant (the
    raw CSV has no assignment rule). All other text is verbatim from the paper
    and build_jsonl.py's transcribe_exp0.

    The DataFrame matches exp0.csv minus the demographic columns ``age`` and
    ``gender``.
    """

    def __init__(self):
        self.name = "gunadi_2022_impact_exp0"
        self.conditions = CONDITIONS
        self.hist = HIST
        self.labels = LABELS

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            cond = str(np.random.choice(self.conditions))
            prompt = ("You are shopping for a flight ticket for your upcoming holidays. "
                      "Only one airline flies directly to your destination, so you must "
                      "fly with it. The airline shows you the ticket's historical prices: "
                      + _history(self.hist[cond], self.labels)
                      + ". Currently, the ticket costs $400.\n"
                      "On each decision you press N if you would buy the ticket now, or W "
                      "if you would wait to buy it later (defer the purchase).")
            if max_chars is None or len(prompt) < max_chars:
                prompt += "\nYou decide whether to buy the $400 ticket now or wait. You press [HUMAN_RESPONSE]"
                token = agent(prompt, choice_options=["N", "W"])
                prompt += f"{token}[/HUMAN_RESPONSE]."
                rows.append({
                    "participant_id": f"P{participant:03d}", "trial": 0,
                    "response": 0 if token == "N" else 1,
                    "variable": VARIABLE[cond], "condition": cond,
                })
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "variable", "condition",
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

    task = FlightDeferral()
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