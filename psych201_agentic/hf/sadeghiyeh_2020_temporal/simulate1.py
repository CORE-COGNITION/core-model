# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas"]
# ///
"""Text simulator for exp1 of ``Hugging-Brain/sadeghiyeh_2020_temporal``
(27-item Delay Discounting Questionnaire), format-identical to the repo's
``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd

# Verbatim from build_jsonl.py (transcribe_exp1).
INSTRUCTIONS = (
    "You will answer 27 questions about money. In each question you choose "
    "between a smaller amount available today and a larger amount available "
    "later. You have a 1 in 4 chance of actually receiving a payment based on "
    "the preferences you indicate; if you do receive payment, the question on "
    "which it is based is chosen at random. The 'today' choice would be paid "
    "out as soon as you complete the study, while the 'later' choice would be "
    "paid out after the number of days indicated in that question. For each "
    "question, press T for 'today' or press L for 'later'.\n"
)

# The 27-item Delay Discounting Questionnaire (Kirby et al. 1999), as used in
# the paper and its task materials: item_id (1..27) -> (today amount, later
# amount, delay days). Verbatim from build_jsonl.py.
MCQ = {
    1: (54, 55, 117), 2: (55, 75, 61), 3: (19, 25, 53), 4: (31, 85, 7),
    5: (14, 25, 19), 6: (47, 50, 160), 7: (15, 35, 13), 8: (25, 60, 14),
    9: (78, 80, 162), 10: (40, 55, 62), 11: (11, 30, 7), 12: (67, 75, 119),
    13: (34, 35, 186), 14: (27, 50, 21), 15: (69, 85, 91), 16: (49, 60, 89),
    17: (80, 85, 157), 18: (24, 35, 29), 19: (33, 80, 14), 20: (28, 30, 179),
    21: (34, 50, 30), 22: (25, 30, 80), 23: (41, 75, 20), 24: (54, 60, 111),
    25: (54, 80, 30), 26: (22, 25, 136), 27: (20, 55, 7),
}


class DelayDiscountingQuestionnaire:
    """Delay Discounting Questionnaire, Experiment 2 of Sadeghiyeh et al.
    (2020), "Temporal discounting correlates with directed exploration but not
    with random exploration", Sci Rep, 10, 4020.

    Design (Methods, "Temporal discounting measure", pp. 2-3): each
    participant answers the 27 items of the Delay Discounting Questionnaire
    (Kirby et al. 1999), choosing on every item between a smaller immediate
    amount ("today") and a larger delayed amount ("later"). The item wording
    is fully verbatim: today amount, later amount, and delay in days are the
    fixed materials (also used by build_jsonl.py::transcribe_exp1).

    The transcript narration is mirrored exactly: each item is marked with the
    chosen token ``T`` (today, response 0) or ``L`` (later, response 1); the
    token mapping is fixed for all participants.

    Questionnaires scores (age, gender, the estimated discounting rates k and
    the today-count) are not producible from the text and are dropped; the
    DataFrame carries ``participant_id``, ``trial``, ``phase``, ``item_id``
    and ``response``.
    """

    def __init__(self):
        self.name = "sadeghiyeh_2020_temporal_exp1"
        self.items = sorted(MCQ)  # item_id 1..27, fixed order

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in range(num_simulations):
            prompt = INSTRUCTIONS
            for trial in range(len(self.items)):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                item = self.items[trial]
                today, later, days = MCQ[item]
                prompt += (f"Question {item}: Would you prefer ${today} today "
                           f"or ${later} in {days} days? You press "
                           f"[HUMAN_RESPONSE]")
                token = agent(prompt, choice_options=["T", "L"])
                prompt += f"{token}[/HUMAN_RESPONSE].\n"
                response = 0 if token == "T" else 1
                rows.append({
                    "participant_id": participant, "trial": trial,
                    "phase": "questionnaire", "item_id": item,
                    "response": response,
                })
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "phase", "item_id", "response",
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

    task = DelayDiscountingQuestionnaire()
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