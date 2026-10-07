# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp4 (Study 5) of ``Hugging-Brain/olschewski_2024_frequent``,
format-identical to the repo's ``transcripts4.jsonl``.

``uv run simulate4.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

INSTRUCTIONS = (
    "In this task you earn points by repeatedly choosing among slot machines. The task "
    "is played as a series of games; each game has its own machines, and the same "
    "machines stay available for the whole game. On each turn you pick one machine; "
    "right after your pick, one draw is revealed for every available machine showing "
    "what it would have paid, and you receive the draw of the machine you chose. "
    "Name each machine by its letter shown on screen. "
    "At the end, one of your turns is chosen randomly and pays your bonus."
)


COND_LABEL = {"catch": "catch", "con": "conskewed", "gauss": "normal",
              "disMatch": "disskewed", "disLess": "disless", "disMore": "dismore"}


def _num(v):
    return f"{float(v):g}"


class BanditGameStudy5:
    """Study 5 (exp4) of Olschewski, Spektor & Le Mens (2024), PNAS 121, e2317751121.

    Design (Supporting Information, Study 5): a repeated multi-armed bandit with six
    games x 30 choices each between two letter-labeled machines, where every choice is
    followed by the revealed draw of every available machine. The conditions match
    Study 4 (single-digit outcomes): a discrete skew pair, an EV-different discrete
    pair ("catch"), a continuous skew pair, a yoked-Gaussian identical pair, and the
    two discrete rare-event frequency conditions. Option letters and screen
    positions are randomized per participant.

    ASSUMPTION (condition set): the per-game marginal distributions are the ones
    measured in exp4.csv; the "gaussian identical" pair is yoked so the frequent
    winner draws the higher outcome in ~20 of the 30 trials; the discrete conditions
    use their observed rare-event rates (0.333, 0.2, 0.067).

    block_no is the game's presentation position (task_id + 1) and ``condition``
    carries the condition label, as in exp4.csv (source block_id 1..6 mapped by the
    authors' Analyses.ipynb).

    The DataFrame matches exp4.csv minus ``rt`` (a text simulator produces no
    reaction times).
    """

    def __init__(self):
        self.name = "olschewski_2024_frequent_exp4"
        self.n_games = 6
        self.n_trials = 30
        self.gauss = {1: 1 / 30, 2: 2 / 30, 3: 4 / 30, 4: 5 / 30,
                      5: 6 / 30, 6: 5 / 30, 7: 4 / 30, 8: 2 / 30, 9: 1 / 30}

    def _draw(self, dist):
        keys = np.array(list(dist.keys()), dtype=float)
        probs = np.array(list(dist.values()), dtype=float)
        probs = probs / probs.sum()
        return int(np.random.choice(keys, p=probs))

    def _cond_dist(self, cond):
        """Return (distA, distB) for a non-yoked condition or None for gauss."""
        if cond == "gauss":
            return None
        if cond == "catch":
            return ({1: 1 / 3, 4: 2 / 3}, {6: 2 / 3, 9: 1 / 3})
        if cond == "con":
            return ({1: 1 / 15, 2: 1 / 30, 3: 1 / 30, 4: 2 / 15, 5: 4 / 15,
                     6: 11 / 30, 7: 1 / 10},
                    {5: 1 / 10, 6: 2 / 15, 7: 11 / 30, 8: 1 / 30, 9: 1 / 15})
        if cond == "disMatch":
            return ({1: 1 / 5, 6: 4 / 5}, {4: 4 / 5, 9: 1 / 5})
        if cond == "disLess":
            return ({1: 1 / 15, 6: 14 / 15}, {4: 14 / 15, 9: 1 / 15})
        if cond == "disMore":
            return ({1: 1 / 3, 6: 2 / 3}, {4: 2 / 3, 9: 1 / 3})

    def _game_draws(self, cond, n):
        """Pre-generate n trials for both option letters of a game."""
        if cond == "gauss":
            a = np.sort([self._draw(self.gauss) for _ in range(n)])
            winner_left = bool(np.random.rand() < 0.5)
            k = 20 if winner_left else 10
            b = np.roll(a, int(n - k)).tolist()
            a = a.tolist()
            return a, b
        da, db = self._cond_dist(cond)
        a = [self._draw(da) for _ in range(n)]
        b = [self._draw(db) for _ in range(n)]
        return a, b

    @staticmethod
    def _positions(n_opt):
        if n_opt == 2:
            return ["left", "right"]
        return ["left", "center", "right"]

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        conds = ["catch", "con", "gauss", "disMatch", "disLess", "disMore"]
        for participant in tqdm(range(num_simulations)):
            pid = participant
            prompt = INSTRUCTIONS
            order = list(conds)
            np.random.shuffle(order)
            for task_id, cond in enumerate(order):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                a, b = self._game_draws(cond, self.n_trials)
                # randomize the letters that label the two machines
                letters = ["A", "B"] if np.random.rand() < 0.5 else ["B", "A"]
                # randomize which position each letter sits at
                pos_names = self._positions(2)
                np.random.shuffle(pos_names)
                pos_of = dict(zip(letters, pos_names))
                outcome = dict(zip(letters, [a, b]))
                prompt += f"\nGame {task_id + 1}:"
                for trial in range(self.n_trials):
                    slot_vals = {l: outcome[l][trial] for l in letters}
                    prompt += (
                        f"\nTurn {trial + 1}: the machines available are "
                        f"{', '.join(sorted(letters))}. "
                        f"You choose [HUMAN_RESPONSE]"
                    )
                    ch = agent(prompt, choice_options=letters)
                    if ch not in letters:
                        ch = letters[0]
                    reward = slot_vals[ch]
                    # position order (left, center, right) governs the "machine pays" listing
                    pos_order = sorted(letters, key=lambda l: ("left", "center", "right").index(pos_of[l]))
                    paid = ", ".join(
                        f"machine {l} pays {_num(slot_vals[l])}" for l in pos_order)
                    prompt += (
                        f"{ch}[/HUMAN_RESPONSE]. "
                        f"That turn {paid}. "
                        f"You receive {_num(reward)}."
                    )
                    # physical option placement (2 machines -> left & right)
                    opts = {"left": "-", "center": "-", "right": "-"}
                    for l in letters:
                        opts[pos_of[l]] = l
                    rows.append({
                        "participant_id": pid, "task_id": task_id, "trial": trial,
                        "choice": ch, "response": int(sorted(letters).index(ch)),
                        "condition": COND_LABEL[cond],
                        "choice_location": pos_of[ch],
                        "outcomeA": slot_vals.get("A"), "outcomeB": slot_vals.get("B"),
                        "outcomeC": slot_vals.get("C", "-"),
                        "chosen_reward": reward,
                        "option_left": opts["left"], "option_center": opts["center"],
                        "option_right": opts["right"], "block_no": task_id + 1,
                        "valid": 1,
                    })
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "task_id", "trial", "choice", "response", "condition",
            "choice_location", "outcomeA", "outcomeB", "outcomeC",
            "chosen_reward", "option_left", "option_center", "option_right",
            "block_no", "valid",
        ])
        return df, prompts


def _random_agent(prompt, choice_options):
    return str(np.random.choice(choice_options))


def main():
    parser = argparse.ArgumentParser(description="Smoke-test this simulator.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3)
    parser.add_argument("--max-chars", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()
    if args.seed is not None:
        np.random.seed(args.seed)
    task = BanditGameStudy5()
    df, prompts = task.simulate(_random_agent, args.num_simulations,
                                max_chars=args.max_chars)
    print(f"name: {task.name}")
    print(f"df shape: {df.shape}")
    print(df.dtypes.to_string())
    print(df.head(8).to_string())
    print(f"prompt lengths: {[len(p) for p in prompts]}")
    for i, p in enumerate(prompts):
        print(f"participant {i} first line: {p.splitlines()[0][:160]}")
    print("=" * 78)
    print("first prompt, tail:")
    print(prompts[0][-400:])


if __name__ == "__main__":
    main()