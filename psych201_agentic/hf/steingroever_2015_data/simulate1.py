# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 of ``Hugging-Brain/steingroever_2015_data``,
format-identical to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
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

# Study -> (sample-size weight, payoff scheme), from exp1.csv / paper Table 1.
STUDIES = [
    ("Horstmann", 162, 2),
    ("Kjome", 19, 3),
    ("Maia", 40, 1),
    ("Premkumar", 25, 3),
    ("SteingroverInPrep", 70, 2),
    ("Wood", 153, 3),
    ("Worthy", 35, 1),
]

# Payoff scheme 1 (traditional IGT; Table A1): wins constant per deck, fixed
# 40-draw loss sequence per deck repeating every 40 draws.
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

# Payoff scheme 2 (Table A2): wins constant per deck; within each deck the 10-card
# block is a fresh random shuffle per block of 10 draws.
BLOCK_LOSS_2 = [
    [0, 0, 0, 0, 0, -150, -200, -250, -300, -350],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, -1250],
    [0, 0, 0, 0, 0, -50, -50, -50, -50, -50],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, -250],
]
WIN_2 = [100, 100, 50, 50]

# Payoff scheme 3 (Bechara & Damasio 2002; Table A3): wins vary within each deck,
# fixed 60-draw sequence per deck; bad decks worsen by -150/block of 10, good
# decks improve by +25/block, so the six-block net goes -250 -> -1000 (A, B) and
# +250 -> +375 (C, D).
WIN_3 = [
    [100, 120, 80, 90, 110, 100, 80, 120, 110, 90, 110, 130, 90, 100, 120, 110,
     90, 130, 120, 100, 120, 140, 110, 110, 100, 120, 130, 110, 140, 120, 130,
     120, 140, 130, 110, 150, 140, 120, 150, 110, 140, 130, 150, 140, 120, 160,
     150, 130, 160, 120, 150, 140, 160, 150, 130, 170, 160, 140, 170, 130],
    [100, 80, 110, 120, 90, 100, 90, 120, 110, 80, 110, 100, 90, 130, 120, 130,
     110, 90, 100, 120, 120, 110, 140, 130, 100, 110, 120, 120, 140, 110, 130,
     140, 120, 110, 130, 150, 110, 150, 120, 140, 140, 150, 130, 120, 140, 160,
     120, 160, 130, 150, 150, 160, 140, 130, 150, 170, 130, 170, 140, 160],
    [50, 60, 40, 55, 55, 45, 50, 45, 60, 40, 55, 55, 65, 45, 70, 40, 50, 60, 70,
     40, 60, 65, 55, 80, 40, 60, 55, 65, 40, 80, 65, 75, 55, 60, 70, 65, 55, 75,
     45, 85, 70, 80, 60, 65, 75, 70, 60, 80, 50, 90, 75, 85, 65, 70, 80, 75, 65,
     85, 55, 95],
    [50, 40, 45, 45, 55, 60, 40, 55, 50, 60, 55, 40, 60, 40, 45, 55, 65, 70, 50,
     70, 60, 55, 65, 80, 40, 80, 40, 65, 55, 60, 65, 75, 60, 65, 75, 85, 45, 55,
     70, 55, 70, 80, 65, 70, 80, 90, 50, 60, 75, 60, 75, 85, 70, 75, 85, 95, 55,
     65, 80, 65],
]
LOSS_3 = [
    [0, 0, -150, 0, -300, 0, -200, 0, -250, -350, 0, -350, 0, -250, -200, 0,
     -300, -150, -250, 0, -250, -300, 0, -350, 0, -200, -250, -150, -250, 0,
     -350, -200, -250, -250, -150, 0, -150, -300, -350, 0, -350, -200, -250,
     -250, -150, 0, -150, -300, -350, -250, -350, -200, -250, -250, -150, -250,
     -150, -300, -350, -250],
    [0, 0, 0, 0, 0, 0, 0, 0, -1250, 0, 0, 0, 0, -1500, 0, 0, 0, 0, 0, 0,
     -1750, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2000, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, -2250, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2500, 0, 0],
    [0, 0, -50, 0, -50, 0, -50, 0, -50, -50, 0, -25, -75, 0, -25, 0, -25, -75,
     0, -50, 0, -25, 0, -50, -25, -50, 0, -25, -75, -50, -25, 0, -25, -25, -25,
     0, -75, -25, -50, -75, -25, 0, -25, -25, -25, -25, -75, -25, -50, -75,
     -25, -25, -25, -25, -25, -25, -75, -25, -50, -75],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, -250, 0, 0, 0, 0, 0, 0, 0, 0, 0, -275,
     0, 0, 0, 0, 0, 0, 0, 0, -300, 0, 0, 0, 0, 0, -325, 0, 0, 0, 0, 0,
     0, 0, 0, 0, -350, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -375, 0, 0],
]


class IowaGamblingTask:
    """Iowa Gambling Task, exp1 of Steingroever et al. (2015), "Data from 617
    healthy participants performing the Iowa gambling task", Journal of Open
    Psychology Data, 3(1), e5. 100-trial group pooling 7 studies.

    Design (Method, Materials, pp. 2-3; Table 1; Supplemental Text 1): the
    participant is loaned $2000 and makes a free deck choice (A-D) on each of 100
    trials, then sees the win and loss of the chosen card. The participant's study
    selects the payoff scheme: scheme 1 (Maia, Worthy) fixed 40-draw loss
    sequences; scheme 2 (Horstmann, SteingroverInPrep) 10-card blocks shuffled
    fresh per block of 10 draws; scheme 3 (Kjome, Premkumar, Wood) Bechara &
    Damasio 2002 fixed 60-draw sequences with within-deck varying wins.

    ASSUMPTION: ``study`` (hence the payoff scheme) is drawn per participant with
    probability proportional to the study's sample size in exp1.csv
    (162/19/40/25/70/153/35), the same choice the repo's jsPsych experiment makes.
    ``participant_id`` is the simulation index and ``source_subject`` its 1-based
    subject number.

    The DataFrame matches exp1.csv (participant_id, source_subject, trial,
    response, deck_choice, win, loss, study) exactly; all columns are produced.
    """

    def __init__(self):
        self.name = "steingroever_2015_data_exp1"
        self.num_trials = 100

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            study = self._pick_study()
            scheme = self._scheme(study)
            decks = self._new_decks(scheme)
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

    def _new_decks(self, scheme):
        if scheme == 1:
            return [_FixedDeck(WIN_1[i], LOSS_1[i]) for i in range(4)]
        if scheme == 2:
            return [_BlockDeck(WIN_2[i], BLOCK_LOSS_2[i]) for i in range(4)]
        return [_SequenceDeck(WIN_3[i], LOSS_3[i]) for i in range(4)]

    def _pick_study(self):
        total = sum(w for _, w, _ in STUDIES)
        r = np.random.rand() * total
        for name, w, _ in STUDIES:
            r -= w
            if r <= 0:
                return name
        return STUDIES[-1][0]

    @staticmethod
    def _scheme(study):
        return next(s for n, _, s in STUDIES if n == study)


class _FixedDeck:
    """A deck whose win/loss schedule is a fixed repeating sequence."""

    def __init__(self, win, losses):
        self.win = win
        self.losses = losses
        self.i = 0

    def next(self):
        w, l = self.win, self.losses[self.i % len(self.losses)]
        self.i += 1
        return w, l


class _SequenceDeck:
    """A deck whose win and loss both vary along a fixed repeating sequence."""

    def __init__(self, wins, losses):
        self.wins = wins
        self.losses = losses
        self.i = 0

    def next(self):
        k = self.i % len(self.losses)
        w, l = self.wins[k], self.losses[k]
        self.i += 1
        return w, l


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