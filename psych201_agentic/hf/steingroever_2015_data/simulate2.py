# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp2 of ``Hugging-Brain/steingroever_2015_data``,
format-identical to the repo's ``transcripts2.jsonl``.

``uv run simulate2.py -n 3`` smoke-tests with a uniform-random agent; or import
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

# Study -> sample-size weight (from exp2.csv); both studies use payoff scheme 2,
# so this is a provenance label only.
STUDIES = [("Steingroever2011", 57), ("Wetzels", 41)]

# Payoff scheme 2 (paper Supplemental Text 1, Table A2): wins constant per deck
# (A=100, B=100, C=50, D=50); within each deck the 10-card block is a fresh
# random shuffle per block of 10 draws.
WIN_2 = [100, 100, 50, 50]
BLOCK_LOSS_2 = [
    [0, 0, 0, 0, 0, -150, -200, -250, -300, -350],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, -1250],
    [0, 0, 0, 0, 0, -50, -50, -50, -50, -50],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, -250],
]


class IowaGamblingTask:
    """Iowa Gambling Task, exp2 of Steingroever et al. (2015), "Data from 617
    healthy participants performing the Iowa gambling task", Journal of Open
    Psychology Data, 3(1), e5. 150-trial group pooling the Steingroever et al.
    2011 and Wetzels et al. studies.

    Design (Method, Materials, pp. 2-3; Table 1; Supplemental Text 1, Table A2):
    the participant is loaned $2000 and makes a free deck choice (A-D) on each of
    150 trials, then sees the win and loss of the chosen card. Both studies use
    payoff scheme 2: wins constant per deck; within each deck the 10-card block
    is a fresh random shuffle per block of 10 draws. Good decks C and D net +250
    per block of 10, bad decks A and B net -250 per block of 10.

    ASSUMPTION: ``study`` is drawn per participant with probability proportional
    to the study's sample size in exp2.csv (Steingroever2011 57 / Wetzels 41);
    it is a provenance label only, as both studies run the identical scheme-2
    payoff. ``participant_id`` is the simulation index and ``source_subject`` its
    1-based subject number.

    The DataFrame matches exp2.csv (participant_id, source_subject, trial,
    response, deck_choice, win, loss, study) exactly; all columns are produced.
    """

    def __init__(self):
        self.name = "steingroever_2015_data_exp2"
        self.num_trials = 150

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            study = self._pick_study()
            decks = [_BlockDeck(WIN_2[i], BLOCK_LOSS_2[i]) for i in range(4)]
            prompt = INSTRUCTIONS
            for trial in range(self.num_trials):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                prompt += "\nYou pick deck [HUMAN_RESPONSE]"
                token = agent(prompt, choice_options=DECK_LETTER)
                deck = DECK_LETTER.index(token)
                win, loss = decks[deck].next()
                prompt += (f"{token}[/HUMAN_RESPONSE]. You win {win}; you lose "
                           f"{abs(loss)}.")
                rows.append({
                    "participant_id": participant, "source_subject": participant + 1,
                    "trial": trial, "response": deck + 1, "deck_choice": deck + 1,
                    "win": float(win), "loss": float(loss), "study": study,
                })
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "source_subject", "trial", "response", "deck_choice",
            "win", "loss", "study",
        ])
        return df, prompts

    def _pick_study(self):
        total = sum(w for _, w in STUDIES)
        r = np.random.rand() * total
        for name, w in STUDIES:
            r -= w
            if r <= 0:
                return name
        return STUDIES[-1][0]


class _BlockDeck:
    """A deck whose 10-card loss block is a fresh random shuffle per block of 10."""

    def __init__(self, win, block_losses):
        self.win = win
        self.block_losses = block_losses
        self.block = block_losses[:]
        self.i = 0
        np.random.shuffle(self.block)

    def next(self):
        if self.i >= len(self.block):
            self.block = self.block_losses[:]
            np.random.shuffle(self.block)
            self.i = 0
        l = self.block[self.i]
        self.i += 1
        return self.win, l


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