# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp4 (Study 4) of ``Hugging-Brain/gunadi_2022_impact``,
format-identical to the repo's ``transcripts4.jsonl``.

``uv run simulate4.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Conditions: 2(direction) x 3(frequency/timing), tablet scenario (paper Study 4,
# "Procedure", pp. 25-26). Historical prices and labels as in build_jsonl.py.
HIST = {
    "dec_single_late": [399, 399, 399, 399, 399],
    "inc_single_late": [199, 199, 199, 199, 199],
    "dec_single_early": [399, 399, 299, 299, 299],
    "inc_single_early": [199, 199, 299, 299, 299],
    "dec_multiple": [399, 379, 359, 339, 319],
    "inc_multiple": [199, 219, 239, 259, 279],
}
LABELS = ["5 weeks ago", "4 weeks ago", "3 weeks ago", "2 weeks ago", "1 week ago"]
CHOICE_VAR = {"dec_single_late": "LowDeLa", "inc_single_late": "LowInLa",
              "dec_single_early": "LowDeEa", "inc_single_early": "LowInEa",
              "dec_multiple": "HighDe", "inc_multiple": "HighIn"}
PRED_VAR = {"dec_single_late": "PredLowDeLa", "inc_single_late": "PredLowInLa",
            "dec_single_early": "PredDeEa", "inc_single_early": "PredInEa",
            "dec_multiple": "PredHighDe", "inc_multiple": "PredHighIn"}
CONDITIONS = list(HIST.keys())


def _usd(v):
    f = float(v)
    return "$" + (str(int(f)) if f.is_integer() else f"{f:.2f}")


def _history(prices, labels):
    return ", ".join(f"{_usd(p)} ({l})" for p, l in zip(prices, labels))


class TabletDeferral:
    """Purchase-deferral task, Study 4 of Gunadi & Evangelidis (2022), "The
    impact of historical price information on purchase deferral", Journal of
    Marketing Research, 59(3), 623-640.

    Design (Study 4, Procedure, pp. 25-26): a between-subjects 2(direction) x
    3(frequency/timing) tablet scenario. The participant buys now (response 0,
    token N) or waits (response 1, token W), then predicts the price in a week
    (open-ended, $0-$500).

    ASSUMPTION: the condition is assigned uniformly at random per participant
    (the raw CSV has no assignment rule). The paper says the two measures were
    shown in random order; the CSV/build_jsonl use choice then prediction,
    which is mirrored here. All other text is verbatim from build_jsonl.py's
    transcribe_exp4.

    The DataFrame matches exp4.csv minus the demographic columns ``age`` and
    ``gender``.
    """

    def __init__(self):
        self.name = "gunadi_2022_impact_exp4"
        self.conditions = CONDITIONS
        self.hist = HIST
        self.labels = LABELS

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            cond = str(np.random.choice(self.conditions))
            hist = _history(self.hist[cond], self.labels)
            prompt = ("You are considering buying a tablet. The tablet's historical price "
                      "was: " + hist + ". Currently, the tablet's price is $299.\n"
                      "On each decision, press N to buy the tablet now, or W to wait "
                      "(buy later).")
            trial = 0
            if max_chars is None or len(prompt) < max_chars:
                prompt += ("\nYou decide whether to buy the tablet now or later. "
                           "You press [HUMAN_RESPONSE]")
                token = agent(prompt, choice_options=["N", "W"])
                prompt += f"{token}[/HUMAN_RESPONSE]."
                rows.append({"participant_id": f"P{participant:03d}", "trial": trial,
                             "response": 0.0 if token == "N" else 1.0,
                             "variable": CHOICE_VAR[cond], "measure": "choice",
                             "condition": cond})
                trial += 1
            if max_chars is None or len(prompt) < max_chars:
                prompt += ("\nYou predict the price of the tablet in a week from now (in $, "
                           "between $0 and $500). You answer [HUMAN_RESPONSE]")
                token = agent(prompt, choice_options=None)
                prompt += f"{token}[/HUMAN_RESPONSE]."
                rows.append({"participant_id": f"P{participant:03d}", "trial": trial,
                             "response": float(token), "variable": PRED_VAR[cond],
                             "measure": "prediction", "condition": cond})
                trial += 1
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "variable", "measure", "condition",
        ])
        return df, prompts


def _random_agent(prompt, choice_options):
    if choice_options is None:
        return str(np.random.randint(0, 500))
    return str(np.random.choice(choice_options))


def main():
    parser = argparse.ArgumentParser(
        description="Smoke-test this simulator with a uniform-random agent.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3, help="number of simulations (default: 3)")
    parser.add_argument("--max-chars", type=int, default=None, help="stop each participant at the block boundary at/past this many chars")
    parser.add_argument("--seed", type=int, default=None, help="numpy random seed, for reproducible runs")
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    task = TabletDeferral()
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