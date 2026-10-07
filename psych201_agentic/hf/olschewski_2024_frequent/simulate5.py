# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp5 (Study 6) of ``Hugging-Brain/olschewski_2024_frequent``,
format-identical to the repo's ``transcripts5.jsonl``.

``uv run simulate5.py -n 3`` smoke-tests with a uniform-random agent; or import
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

POSITIONS = ("left", "center", "right")


COND_LABEL = {"discrete": "disskewed", "continuous": "consskewed", "gauss": "normal",
              "continuous+decoy": "consskewed_tri", "gauss+decoy": "normal_tri",
              "three": "disskewedthree"}


def _num(v):
    return f"{float(v):g}"


class BanditGameStudy6:
    """Study 6 (exp5) of Olschewski, Spektor & Le Mens (2024), PNAS 121, e2317751121.

    Design (Supporting Information, Study 6): repeated multi-armed bandit, six games
    x 30 choices, choice sets of two or three letter-labeled machines. The conditions
    replicate Study 1 in the bandit paradigm: a discrete skew pair, a continuous skew
    pair, a yoked-Gaussian identical pair, the same pairs with an inferior Gaussian
    decoy added (three options), and a three-equally-probable-outcome pair.

    ASSUMPTION (dists): continuous options draw per turn from a game-level set of 30
    skewed gamma "quantile" values (mirrored for the two skew directions); the Gaussian
    identical pair is yoked so the frequent winner draws the higher outcome in 20 of
    the 30 turns; the decoy is an inferior Gaussian ~30 points below the core.

    block_no is the game's presentation position (task_id + 1) and ``condition``
    carries the condition label, as in exp5.csv (source block_id 1..6 mapped by the
    authors' Analyses.ipynb).

    The DataFrame matches exp5.csv minus ``rt``.
    """

    def __init__(self):
        self.name = "olschewski_2024_frequent_exp5"
        self.n_games = 6
        self.n_trials = 30
        self.sd = 30.0

    @staticmethod
    def _quantile_set(mean, sd, skew):
        g = np.sort(np.random.gamma(0.5, 1.0, 30))
        if skew == "left":
            g = -g[::-1]
        v = np.round((g - g.mean()) / g.std() * sd + mean).astype(int)
        return v.tolist()

    @staticmethod
    def _draw(values):
        return int(np.random.choice(list(values)))

    def _sets_for(self, cond, n_opt):
        if cond == "discrete":
            return {0: [171, 225], 1: [135, 189]}
        if cond == "continuous":
            return {0: self._quantile_set(180.0, self.sd, "left"),
                    1: self._quantile_set(180.0, self.sd, "right")}
        if cond == "gauss":
            base = self._quantile_set(180.0, self.sd, "left")
            return {0: base, 1: base}
        if cond == "continuous+decoy":
            return {0: self._quantile_set(180.0, self.sd, "left"),
                    1: self._quantile_set(180.0, self.sd, "right"),
                    2: self._quantile_set(150.0, self.sd, "left")}
        if cond == "gauss+decoy":
            base = self._quantile_set(180.0, self.sd, "left")
            return {0: base, 1: base, 2: self._quantile_set(150.0, self.sd, "left")}
        return {0: [164, 166, 207], 1: [151, 192, 194]}   # three-outcome

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        conds = [("discrete", 2), ("continuous", 2), ("gauss", 2),
                 ("continuous+decoy", 3), ("gauss+decoy", 3), ("three", 2)]
        for participant in tqdm(range(num_simulations)):
            pid = participant
            prompt = INSTRUCTIONS
            order = list(conds)
            np.random.shuffle(order)
            for task_id, (cond, n_opt) in enumerate(order):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                letters = list("ABC")[:n_opt]
                np.random.shuffle(letters)
                sets = self._sets_for(cond, n_opt)   # keyed by 0..n_opt-1
                # roll per-letter outcome sequences for the whole game
                seqs = {l: [self._draw(sets[i]) for _ in range(self.n_trials)]
                        for i, l in enumerate(letters)}
                if cond in ("gauss", "gauss+decoy"):
                    # identical pair: yoked so a designated winner leads 20/30
                    base = sorted(seqs[letters[0]])
                    winner = letters[0] if bool(np.random.rand() < 0.5) else letters[1]
                    k = 20 if winner == letters[0] else 10
                    seqs[letters[0]] = base
                    seqs[letters[1]] = np.roll(np.array(base), int(self.n_trials - k)).tolist()
                pos_names = list(POSITIONS[:n_opt])
                np.random.shuffle(pos_names)
                pos_of = dict(zip(letters, pos_names))
                prompt += f"\nGame {task_id + 1}:"
                for trial in range(self.n_trials):
                    slot = {l: seqs[l][trial] for l in letters}
                    prompt += (
                        f"\nTurn {trial + 1}: the machines available are "
                        f"{', '.join(sorted(letters))}. "
                        f"You choose [HUMAN_RESPONSE]"
                    )
                    ch = agent(prompt, choice_options=letters)
                    if ch not in letters:
                        ch = letters[0]
                    reward = slot[ch]
                    pos_order = sorted(letters, key=lambda l: POSITIONS[:n_opt].index(pos_of[l]))
                    paid = ", ".join(f"machine {l} pays {_num(slot[l])}" for l in pos_order)
                    prompt += (
                        f"{ch}[/HUMAN_RESPONSE]. "
                        f"That turn {paid}. "
                        f"You receive {_num(reward)}."
                    )
                    opts = {p: "-" for p in POSITIONS}
                    for l in letters:
                        opts[pos_of[l]] = l
                    rows.append({
                        "participant_id": pid, "task_id": task_id, "trial": trial,
                        "choice": ch, "response": int(sorted(letters).index(ch)),
                        "condition": COND_LABEL[cond],
                        "choice_location": pos_of[ch],
                        "outcomeA": slot.get("A"), "outcomeB": slot.get("B"),
                        "outcomeC": slot.get("C", "-"),
                        "chosen_reward": reward,
                        "option_left": opts["left"], "option_center": opts["center"],
                        "option_right": opts["right"],
                        "block_no": task_id + 1, "valid": 1,
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
    task = BanditGameStudy6()
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