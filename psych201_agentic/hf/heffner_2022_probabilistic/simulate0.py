# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/heffner_2022_probabilistic``
(Ultimatum Game), format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp0 + GRID).
GRID = ("On an affect grid you report how you feel by typing two integers: "
        "first your valence rating, an integer from -250 (extremely unpleasant) "
        "to +250 (extremely pleasant); then your arousal rating, an integer from "
        "-250 (very calm) to +250 (very aroused).")
INSTRUCTIONS = (
    "You will play 20 one-shot rounds of the Ultimatum Game as the Responder. "
    "Each round you are paired with a new Proposer who receives $1 and splits it "
    "with you: the Proposer keeps part of it and offers you the rest. After you "
    "see the offer, " + GRID +
    " Then you decide whether to accept the offer (type A) or reject it "
    "(type R), in which case neither of you receives anything.")
GRID_CHOICES = [str(x) for x in range(-250, 251)]


class UltimatumGame:
    """Experiment 1 of Heffner, Son, & FeldmanHall (2022), "A probabilistic
    map of emotional experiences during competitive social interactions",
    Nature Communications 13, 1718. Ultimatum Game as Responder.

    Design (Methods, Ultimatum game, p. 9; Fig. 1B): 20 one-shot rounds, each
    against a new Proposer who keeps part of a $1 pot and offers you the rest.
    After each offer the participant rates their affect on the valence-arousal
    grid, then decides to accept (A) or reject (R). Offers are an even
    distribution from fair ($0.50/$0.50) to highly unfair ($0.95/$0.05): the
    amount kept (unfairness) is drawn uniformly from {0.50, 0.55, ..., 0.95} so
    each of the 10 levels appears exactly twice across the 20 rounds.

    ASSUMPTION: the order of offers within a participant is a random
    permutation of the 20 draws (= 10 levels x 2); the paper only specifies the
    "even distribution" of offer types, not the presentation order.

    The token mapping is fixed, exactly as in build_jsonl.py: A = accept
    (response 0), R = reject (response 1).

    The DataFrame matches exp0.csv (unfairness, valence, arousal, study,
    participant_id, trial, response).
    """

    def __init__(self):
        self.name = "heffner_2022_probabilistic_exp0"
        self.num_rounds = 20
        self.levels = [round(0.5 + 0.05 * i, 2) for i in range(10)]  # 0.50..0.95
        self.study = "ug"

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        offers = self.levels * (self.num_rounds // len(self.levels))
        for participant in tqdm(range(num_simulations)):
            prompt = INSTRUCTIONS
            order = np.random.permutation(offers)
            for trial in range(self.num_rounds):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                unfair = float(order[trial])
                offered = round(1.0 - unfair, 2)
                line = (f"A proposer keeps ${unfair:.2f} and offers you "
                        f"${offered:.2f}. ")
                line += ("You rate how you feel on the affect grid: "
                         "valence [HUMAN_RESPONSE]")
                v = agent(prompt + "\n" + line, choice_options=GRID_CHOICES)
                line += f"{v}[/HUMAN_RESPONSE], arousal [HUMAN_RESPONSE]"
                a = agent(prompt + "\n" + line, choice_options=GRID_CHOICES)
                line += f"{a}[/HUMAN_RESPONSE]. "
                line += "You press [HUMAN_RESPONSE]"
                token = agent(prompt + "\n" + line, choice_options=["A", "R"])
                label = "accept" if token == "A" else "reject"
                response = 0.0 if token == "A" else 1.0
                line += f"{token}[/HUMAN_RESPONSE] ({label})."
                prompt += "\n" + line
                rows.append({
                    "unfairness": unfair, "valence": int(v), "arousal": int(a),
                    "study": self.study, "participant_id": f"P{participant:03d}",
                    "trial": trial, "response": response,
                })
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "unfairness", "valence", "arousal", "study",
            "participant_id", "trial", "response",
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

    task = UltimatumGame()
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