# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/steingroever_2015_data``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_igt); the response token is the deck
# letter itself (A=1, B=2, C=3, D=4), fixed across participants.
INSTRUCTIONS = (
    "You are taking part in the Iowa gambling task. You are given a loan of "
    "$2000 in play money. In front of you are four decks of cards, labeled A, B, "
    "C, and D. On each trial you pick one card from one of the four decks by "
    "pressing the letter of that deck: A, B, C, or D. After each choice you win "
    "some money, and sometimes you also lose some money. Some decks are better "
    "overall than others. Your goal is to win as much money as possible, so choose "
    "the decks you think are best.")
DECK_LETTER = ["A", "B", "C", "D"]

# Payoff scheme 1 (traditional IGT; paper Supplemental Text 1, Table A1; used by
# the 95-trial Fridberg group, exp0). Wins constant per deck (A=100, B=100, C=50,
# D=50); a FIXED 40-draw loss sequence per deck that repeats every 40 draws.
LOSS_1 = [
    [0, 0, -150, 0, -300, 0, -200, 0, -250, -350, 0, -350, 0, -250, -200, 0,
     -300, -150, 0, 0, 0, -300, 0, -350, 0, -200, -250, -150, 0, 0, -350, -200,
     -250, 0, 0, 0, -150, -300, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, -1250, 0, 0, 0, 0, -1250, 0, 0, 0, 0, 0, 0,
     -1250, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1250, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, -50, 0, -50, 0, -50, 0, -50, -50, 0, -25, -75, 0, 0, 0, -25, -75,
     0, -50, 0, 0, 0, -50, -25, -50, 0, 0, -75, -50, 0, 0, 0, -25, -25, 0,
     -75, 0, -50, -75],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, -250, 0, 0, 0, 0, 0, 0, 0, 0, 0, -250,
     0, 0, 0, 0, 0, 0, 0, 0, -250, 0, 0, 0, 0, 0, -250, 0, 0, 0, 0, 0],
]
WIN_1 = [100, 100, 50, 50]


class IowaGamblingTask:
    """Iowa Gambling Task, exp0 of Steingroever et al. (2015), "Data from 617
    healthy participants performing the Iowa gambling task", Journal of Open
    Psychology Data, 3(1), e5. 95-trial group (all from the Fridberg study).

    Design (Method, Materials, pp. 2-3; Supplemental Text 1, Table A1): the
    participant is loaned $2000 and makes a free deck choice (A-D) on each of 95
    trials, then sees the win and loss of the chosen card. Good decks C and D pay
    50 per draw and net +250 per block of 10; bad decks A and B pay 100 per draw
    and net -250 per block of 10. Payoff scheme 1 uses a fixed 40-draw loss
    sequence per deck, repeating every 40 draws from that deck.

    The DataFrame matches exp0.csv (participant_id, source_subject, trial,
    response, deck_choice, win, loss, study) exactly; all columns are produced.
    ``participant_id`` is the simulation index and ``source_subject`` its 1-based
    subject number; win/loss are emitted as float to match the repo's dtypes.
    """

    def __init__(self):
        self.name = "steingroever_2015_data_exp0"
        self.num_trials = 95
        self.study = "Fridberg"

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            draw = [0, 0, 0, 0]
            prompt = INSTRUCTIONS
            for trial in range(self.num_trials):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                prompt += "\nYou pick deck [HUMAN_RESPONSE]"
                token = agent(prompt, choice_options=DECK_LETTER)
                deck = DECK_LETTER.index(token)
                k = draw[deck]
                draw[deck] = k + 1
                win, loss = WIN_1[deck], LOSS_1[deck][k % 40]
                prompt += (f"{token}[/HUMAN_RESPONSE]. You win {win}; you lose "
                           f"{abs(loss)}.")
                rows.append({
                    "participant_id": participant, "source_subject": participant + 1,
                    "trial": trial, "response": deck + 1, "deck_choice": deck + 1,
                    "win": float(win), "loss": float(loss), "study": self.study,
                })
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "source_subject", "trial", "response", "deck_choice",
            "win", "loss", "study",
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

    task = IowaGamblingTask()
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