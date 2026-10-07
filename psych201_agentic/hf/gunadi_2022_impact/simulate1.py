# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 (Study 1b) of ``Hugging-Brain/gunadi_2022_impact``,
format-identical to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Conditions: 2(direction) x 2(frequency), sequential TV scenario (paper Study 1b,
# pp. 15-17). Page prices and dates as in build_jsonl.py.
PAGES = {
    "dec_single": [1200, 900, 900, 900],
    "dec_multiple": [1200, 1100, 1000, 900],
    "inc_single": [1200, 1500, 1500, 1500],
    "inc_multiple": [1200, 1300, 1400, 1500],
}
DATES = ["January 16, 2021", "January 17, 2021", "January 18, 2021", "January 19, 2021"]
COND_PREFIX = {"dec_single": "DL", "dec_multiple": "DH",
               "inc_single": "IL", "inc_multiple": "IH"}
CONDITIONS = list(PAGES.keys())


def _usd(v):
    f = float(v)
    return "$" + (str(int(f)) if f.is_integer() else f"{f:.2f}")


class SequentialTVDeferral:
    """Purchase-deferral task, Study 1b of Gunadi & Evangelidis (2022), "The
    impact of historical price information on purchase deferral", Journal of
    Marketing Research, 59(3), 623-640.

    Design (Study 1b, pp. 15-17): a between-subjects 2(direction) x 2(frequency)
    TV-purchase scenario shown page by page. On each page the participant sees
    the price history up to that date and chooses to buy now (response 0, token
    N), which ends the study, or wait (response 1, token W), which advances to
    the next page. There are four pages total; the study ends after page 4
    (index 3) regardless of choice.

    ASSUMPTION: the condition is drawn uniformly at random per participant (the
    raw CSV has no assignment rule). All other text is verbatim from the paper
    and build_jsonl.py's transcribe_exp1.

    The DataFrame matches exp1.csv minus the demographic columns ``age`` and
    ``gender``.
    """

    def __init__(self):
        self.name = "gunadi_2022_impact_exp1"
        self.conditions = CONDITIONS
        self.pages = PAGES
        self.dates = DATES
        self.num_pages = 4

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            cond = str(np.random.choice(self.conditions))
            prices = self.pages[cond]
            prompt = ("Prices of products change frequently over time. You are considering "
                      "buying a new TV that you have been checking the price of over the "
                      "past days. You will be told the price of the TV at different points "
                      "in time, page by page. On each page you press N to buy the TV now "
                      "(which ends the study for you), or W to wait (buy later) and see the "
                      "next price update.")
            for page in range(self.num_pages):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                hist = [(self.dates[d], prices[d]) for d in range(page + 1)]
                prompt += ("\n" + " ".join(f"On {d} the price of the TV was {_usd(p)}."
                                           for d, p in hist)
                           + f" Currently the price is {_usd(prices[page])}."
                           + " You press [HUMAN_RESPONSE]")
                token = agent(prompt, choice_options=["N", "W"])
                prompt += f"{token}[/HUMAN_RESPONSE]."
                response = 0 if token == "N" else 1
                if response == 0:
                    prompt += " The study ends because you buy now."
                rows.append({
                    "participant_id": f"P{participant:03d}", "trial": page, "response": response,
                    "variable": f"{COND_PREFIX[cond]}{page + 1}", "page": page,
                    "condition": cond,
                })
                if response == 0:
                    break
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "variable", "page", "condition",
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

    task = SequentialTVDeferral()
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