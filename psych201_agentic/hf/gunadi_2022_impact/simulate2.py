# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp2 (Study 2) of ``Hugging-Brain/gunadi_2022_impact``,
format-identical to the repo's ``transcripts2.jsonl``.

``uv run simulate2.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Conditions: 2(direction) x 2(frequency), Bluetooth-speaker scenario (paper
# Study 2, "Procedure", pp. 18-19). Historical prices as in build_jsonl.py.
HIST = {
    "dec_single": [100, 100, 100, 100],
    "dec_multiple": [100, 90, 80, 70],
    "inc_single": [20, 20, 20, 20],
    "inc_multiple": [20, 30, 40, 50],
}
LABELS = ["4 weeks ago", "3 weeks ago", "2 weeks ago", "1 week ago"]
BASE = {"dec_single": "DecLow", "dec_multiple": "DecHigh",
        "inc_single": "IncLow", "inc_multiple": "IncHigh"}
CONDITIONS = list(HIST.keys())


def _usd(v):
    f = float(v)
    return "$" + (str(int(f)) if f.is_integer() else f"{f:.2f}")


def _history(prices, labels):
    return ", ".join(f"{_usd(p)} ({l})" for p, l in zip(prices, labels))


class SpeakerDeferral:
    """Purchase-deferral task, Study 2 of Gunadi & Evangelidis (2022), "The
    impact of historical price information on purchase deferral", Journal of
    Marketing Research, 59(3), 623-640.

    Design (Study 2, Procedure, pp. 18-19): a between-subjects 2(direction) x
    2(frequency) Bluetooth-speaker scenario. The participant first chooses to
    buy now (response 0, token N) or wait (response 1, token W); then rates
    agreement (1-7) with the belief that the price will continue in the same
    direction; then predicts the price in a week (open-ended, $0-$150).

    ASSUMPTION: the condition is drawn uniformly at random per participant (the
    raw CSV has no assignment rule). The paper says the two process measures
    were shown in random order; the transcription/build_jsonl and the CSV use
    the fixed order choice, agreement, prediction, which this simulator mirrors.
    All other text is verbatim from build_jsonl.py's transcribe_exp2.

    The DataFrame matches exp2.csv minus the demographic columns ``age`` and
    ``gender``.
    """

    def __init__(self):
        self.name = "gunadi_2022_impact_exp2"
        self.conditions = CONDITIONS
        self.hist = HIST
        self.labels = LABELS

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            cond = str(np.random.choice(self.conditions))
            hist = _history(self.hist[cond], self.labels)
            base = BASE[cond]
            direction = ("continue to decrease" if cond.startswith("dec")
                         else "continue to increase")
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
                response = 0.0 if token == "N" else 1.0
                rows.append({"participant_id": f"P{participant:03d}", "trial": trial,
                             "response": response, "variable": base,
                             "measure": "choice", "condition": cond})
                trial += 1
            # agreement
            if max_chars is None or len(prompt) < max_chars:
                prompt += (f"\nRate your agreement that '{direction} in the future' on a "
                           f"scale from 1 (strongly disagree) to 7 (strongly agree). "
                           "You answer [HUMAN_RESPONSE]")
                token = agent(prompt, choice_options=["1", "2", "3", "4", "5", "6", "7"])
                prompt += f"{token}[/HUMAN_RESPONSE]."
                rows.append({"participant_id": f"P{participant:03d}", "trial": trial,
                             "response": float(token), "variable": f"Temp{base}_1",
                             "measure": "agreement", "condition": cond})
                trial += 1
            # prediction
            if max_chars is None or len(prompt) < max_chars:
                prompt += ("\nEstimate the price of the speaker in a week from now (in $, "
                           "between $0 and $150). You answer [HUMAN_RESPONSE]")
                token = agent(prompt, choice_options=None)
                prompt += f"{token}[/HUMAN_RESPONSE]."
                rows.append({"participant_id": f"P{participant:03d}", "trial": trial,
                             "response": float(token), "variable": f"Pred{base}",
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

    task = SpeakerDeferral()
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