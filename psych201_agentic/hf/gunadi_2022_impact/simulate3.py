# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp3 (Study 3) of ``Hugging-Brain/gunadi_2022_impact``,
format-identical to the repo's ``transcripts3.jsonl``.

``uv run simulate3.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Conditions: 2(direction) x 3(frequency) including monotonic/nonmonotonic
# multiple changes (paper Study 3, "Procedure", pp. 22-23). Historical prices
# and labels as in build_jsonl.py.
HIST = {
    "dec_single": [100, 100, 100, 100],
    "inc_single": [20, 20, 20, 20],
    "dec_monotonic": [100, 90, 80, 70],
    "inc_monotonic": [20, 30, 40, 50],
    "dec_nonmonotonic": [100, 90, 80, 70, 80],
    "inc_nonmonotonic": [20, 30, 40, 50, 40],
}
LABELS = ["4 weeks ago", "3 weeks ago", "2 weeks ago", "1 week ago", "4 days ago"]
CHOICE_VAR = {"inc_monotonic": "IncHighMo", "inc_single": "IncLow",
              "dec_monotonic": "DecHighMo", "dec_single": "DecLow",
              "dec_nonmonotonic": "DecHighNon", "inc_nonmonotonic": "IncHighNon"}
PRED_VAR = {"inc_monotonic": "PredIncHigh", "inc_single": "PredIncLow",
            "dec_monotonic": "PredDecHighMo", "dec_single": "PredDecLow",
            "dec_nonmonotonic": "PredDecHighNon", "inc_nonmonotonic": "PredIncHighNon"}
CONDITIONS = list(HIST.keys())


def _usd(v):
    f = float(v)
    return "$" + (str(int(f)) if f.is_integer() else f"{f:.2f}")


def _history(prices, labels):
    return ", ".join(f"{_usd(p)} ({l})" for p, l in zip(prices, labels))


class SpeakerMonotonicDeferral:
    """Purchase-deferral task, Study 3 of Gunadi & Evangelidis (2022), "The
    impact of historical price information on purchase deferral", Journal of
    Marketing Research, 59(3), 623-640.

    Design (Study 3, Procedure, pp. 22-23): a between-subjects 2(direction) x
    3(frequency) Bluetooth-speaker scenario testing monotonicity. The
    participant buys now (response 0, token N) or waits (response 1, token W),
    then predicts the price in a week (open-ended, $0-$150).

    ASSUMPTION: the condition is assigned uniformly at random per participant
    (the raw CSV has no assignment rule). The paper says the choice and
    prediction measures are shown in a fixed order; the CSV/build_jsonl use
    choice then prediction, which is mirrored here. All other text is verbatim
    from build_jsonl.py's transcribe_exp3.

    The DataFrame matches exp3.csv minus the demographic columns ``age`` and
    ``gender``.
    """

    def __init__(self):
        self.name = "gunadi_2022_impact_exp3"
        self.conditions = CONDITIONS
        self.hist = HIST
        self.labels = LABELS

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            cond = str(np.random.choice(self.conditions))
            prices = self.hist[cond]
            hist = _history(prices, self.labels[:len(prices)])
            prompt = ("You are considering buying a Bluetooth speaker that you have been "
                      "checking the price of over the past weeks. The speaker's historical "
                      "price was: " + hist + ". Currently, the speaker's price is $60.\n"
                      "On each decision, press N to buy the speaker now, or W to wait "
                      "(buy later).")
            trial = 0
            # choice
            if max_chars is None or len(prompt) < max_chars:
                prompt += ("\nYou decide whether to buy the speaker now or later. "
                           "You press [HUMAN_RESPONSE]")
                token = agent(prompt, choice_options=["N", "W"])
                prompt += f"{token}[/HUMAN_RESPONSE]."
                rows.append({"participant_id": f"P{participant:03d}", "trial": trial,
                             "response": 0.0 if token == "N" else 1.0,
                             "variable": CHOICE_VAR[cond], "measure": "choice",
                             "condition": cond})
                trial += 1
            # prediction
            if max_chars is None or len(prompt) < max_chars:
                prompt += ("\nYou predict the price of the speaker in a week from now (in $, "
                           "between $0 and $150). You answer [HUMAN_RESPONSE]")
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
        return str(np.random.randint(0, 150))
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

    task = SpeakerMonotonicDeferral()
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