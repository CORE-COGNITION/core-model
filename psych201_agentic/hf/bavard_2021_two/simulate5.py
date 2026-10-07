# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp5 of ``Hugging-Brain/bavard_2021_two``, format-identical
to the repo's ``transcripts5.jsonl``.

``uv run simulate5.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py.
INTRO = "Welcome. You are about to take part in an economic decision-making task. You will repeatedly see two abstract symbols on the screen, one on the left and one on the right. Each symbol is associated with points: some symbols can earn you 10 points, others can earn you 1 point, and on every trial you can earn the symbol's full value or 0 points. Your task is to learn, by trial and error, which symbols pay more. On each trial, two symbols appear. Click on the symbol of your choice. After your choice, the outcome is revealed: you see the number of points you won on that trial. The possible outcomes are 0, 1, and 10 points. Your final payoff depends on the points you earn (1 point = 0.005 GBP). Press L to choose the left symbol or R to choose the right symbol."

TRANSFER_INTRO = 'The learning phase is over. You now start the transfer phase: you will see the same symbols as before, only now they are paired differently. The pairs may not be the same as before. Keep choosing the symbol you think is better. Press L to choose the left symbol or R to choose the right symbol.'

# Symbol (1-8) -> point magnitude (10 or 1), fixed across the whole session.
MAGNITUDE = {1: 10, 2: 10, 3: 10, 4: 10, 5: 1, 6: 1, 7: 1, 8: 1}
# Symbol (1-8) -> probability of the positive outcome (0.75 / 0.25), fixed.
WIN_PROB = {1: .75, 2: .25, 3: .75, 4: .25, 5: .75, 6: .25, 7: .75, 8: .25}
# Learning-phase contexts: the two symbols presented together.
LEARNING_PAIRS = {1: (1, 2), 2: (3, 4), 3: (5, 6), 4: (7, 8)}
# Transfer-phase contexts: the same symbols re-paired across reward magnitudes.
TRANSFER_PAIRS = {5: (1, 5), 6: (2, 6), 7: (3, 8), 8: (4, 7)}
# Expected-value-maximizing symbol per context ("correct" choice).
CORRECT_SYMBOL = {1: 1, 2: 3, 3: 5, 4: 7, 5: 1, 6: 2, 7: 3, 8: 4}
CONTEXT_LABEL = {
    1: "7.50_vs_2.50_learning", 2: "7.50_vs_2.50_learning",
    3: "0.75_vs_0.25_learning", 4: "0.75_vs_0.25_learning",
    5: "7.50_vs_0.75_transfer", 6: "2.50_vs_0.25_transfer",
    7: "7.50_vs_0.25_transfer", 8: "2.50_vs_0.75_transfer",
}


def _fmt_points(pts):
    return f"{pts} point" + ("" if pts == 1 else "s")


class ProbabilisticLearningTask:
    """Probabilistic instrumental learning task of Bavard, Rustichini, &
Palminteri (2021), "Two sides of the same coin: beneficial and detrimental
consequences of range adaptation in human reinforcement learning", Science
Advances 7(14):eabe0340, experiment exp5.

Design (Methods, "Experimental protocol", pp. 2-3): eight abstract symbols
(1-8) are presented in pairs. Symbols 1-4 pay 10 points, symbols 5-8 pay 1
point; each symbol yields its full value with probability 0.75 (odd-indexed)
or 0.25 (even-indexed) and 0 otherwise. A short training/familiarization
phase is followed by a 120-trial learning phase (4 contexts x 30 trials) and
a 120-trial transfer phase in which the symbols are re-paired across reward
magnitudes. The pairing of symbols to learning contexts and their win
probabilities is fixed across participants.

The session structure is identical across all eight experiments; exp5 differs
only in trial structure (blocked context order) and feedback display
(partial feedback, feedback in the transfer phase). The task is narrated as in the repo's build_jsonl.py, gating the
chosen outcome (and, in the complete-feedback experiments, the unchosen
outcome) on the experiment design.

ASSUMPTION: the familiarization length is drawn per participant as 12 or 24
trials (6 or 12 per context) with probabilities 0.93/0.07, matching the
observed distribution in the shipped CSVs.
ASSUMPTION: the left/right placement of the two symbols is randomized per
trial with p=0.5 (no counterbalancing), mirroring the raw data.
ASSUMPTION: cumulated_reward starts at 0 for the training phase, resets to 0
at the start of the learning phase, and then continues into the transfer
phase without resetting (matches the observed running totals).
ASSUMPTION: the agent always responds (valid = 1); the occasional missed
trials of the real data are not simulated.

The DataFrame matches exp5.csv minus ``rt`` and the ``age/sex/gender``
demographics (not producible from a text transcript).
"""

    def __init__(self):
        self.name = "bavard_2021_two_exp5"
        self.exp_index = 5
        self.complete_feedback = False
        self.transfer_feedback = True
        self.interleaved = False
        self.trial_order = 2
        self.trials_per_context = 30
        self.learn_contexts = [1, 2, 3, 4]
        self.transfer_contexts = [5, 6, 7, 8]

    def _context_sequence(self, contexts):
        n = self.trials_per_context
        if self.interleaved:
            seq = []
            for c in contexts:
                seq += [c] * n
            np.random.shuffle(seq)
            return seq
        order = list(contexts)
        np.random.shuffle(order)
        seq = []
        for c in order:
            seq += [c] * n
        return seq

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            k = int(np.random.choice([6, 12], p=[0.93, 0.07]))  # familiarization per context
            orders = [("training", c) for c in [1] * k + [3] * k]
            orders += [("learning", c) for c in self._context_sequence(self.learn_contexts)]
            orders += [("transfer", c) for c in self._context_sequence(self.transfer_contexts)]
            # group consecutive (phase, context) into blocks for max_chars
            runs, last = [], None
            for phase, ctx in orders:
                if last == (phase, ctx):
                    runs[-1].append((phase, ctx))
                else:
                    runs.append([(phase, ctx)])
                    last = (phase, ctx)

            prompt = INTRO
            transfer_seen = False
            train_cum = 0
            main_cum = 0
            n_train = k * 2
            t_train = t_learn = t_transfer = 0
            for run in runs:
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                for phase, context in run:
                    if phase == "transfer":
                        pairs = TRANSFER_PAIRS
                    else:  # training and learning
                        pairs = LEARNING_PAIRS
                    a, b = pairs[context]
                    if np.random.rand() < 0.5:
                        left, right = a, b
                    else:
                        left, right = b, a
                    out_left = 1.0 if np.random.rand() < WIN_PROB[left] else 0.0
                    out_right = 1.0 if np.random.rand() < WIN_PROB[right] else 0.0

                    if phase == "transfer" and not transfer_seen:
                        prompt += "\n" + TRANSFER_INTRO
                        transfer_seen = True
                    if phase == "training":
                        trial_no, trial_orig = t_train, t_train
                    elif phase == "learning":
                        trial_no, trial_orig = n_train + t_learn, t_learn
                    else:
                        trial_no, trial_orig = t_transfer, t_transfer

                    prompt += (
                        f"\nTrial {trial_no}: symbol {left} is on the left and "
                        f"symbol {right} is on the right. You press [HUMAN_RESPONSE]"
                    )
                    side = agent(prompt, choice_options=["L", "R"])
                    response = 0 if side == "L" else 1
                    chosen = left if response == 0 else right
                    unchosen = right if response == 0 else left
                    co = out_left if response == 0 else out_right
                    uo = out_right if response == 0 else out_left
                    prompt += f"{side}[/HUMAN_RESPONSE]."

                    show_fb = (phase != "transfer") or self.transfer_feedback
                    if show_fb:
                        pts_chosen = MAGNITUDE[chosen] if co == 1 else 0
                        prompt += f" You earn {_fmt_points(pts_chosen)}."
                        if self.complete_feedback:
                            pts_unchosen = MAGNITUDE[unchosen] if uo == 1 else 0
                            prompt += f" The other symbol would have paid {_fmt_points(pts_unchosen)}."

                    if phase == "training":
                        train_cum += MAGNITUDE[chosen] if co == 1 else 0
                        cum = train_cum
                    else:
                        main_cum += MAGNITUDE[chosen] if co == 1 else 0
                        cum = main_cum

                    rows.append({
                        "participant_id": f"P{participant:03d}",
                        "task_id": 0 if phase != "transfer" else 1,
                        "phase": phase,
                        "trial": trial_no,
                        "context": context,
                        "context_label": CONTEXT_LABEL[context],
                        "left_symbol": float(left),
                        "right_symbol": float(right),
                        "choice_set": f"[{left}, {right}]",
                        "response": float(response),
                        "correct": 1.0 if chosen == CORRECT_SYMBOL[context] else 0.0,
                        "outcome_chosen": float(co),
                        "outcome_unchosen": float(uo),
                        "cumulated_reward": float(cum),
                        "trial_original": trial_orig,
                        "trial_order": self.trial_order,
                        "valid": 1,
                    })
                    if phase == "training":
                        t_train += 1
                    elif phase == "learning":
                        t_learn += 1
                    else:
                        t_transfer += 1
            prompts.append(prompt)

        df = pd.DataFrame(rows, columns=[
            "participant_id", "task_id", "phase", "trial", "context", "context_label",
            "left_symbol", "right_symbol", "choice_set", "response", "correct",
            "outcome_chosen", "outcome_unchosen", "cumulated_reward", "trial_original",
            "trial_order", "valid",
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

    task = ProbabilisticLearningTask()
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
