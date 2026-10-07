# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/vandendriessche_2022_contextual``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import itertools
import random

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (learning_header), with the letter slots kept.
INSTRUCTIONS = (
    "You are playing a computer game and your goal is to earn as many points as "
    "possible. On the black screen two abstract symbols appear, side by side. One of "
    "the two symbols is the better one and you must learn which it is through trial "
    "and error; the reward probability attached to each symbol is never told to you. "
    "Here the symbols are called symbol 1 to symbol 8. "
    "On each trial press a key to pick the left or the right symbol. "
    "Press {left} to pick the left symbol and {right} to pick the "
    "right symbol. "
    "After every choice you get "
    "feedback: a green smiley face with '+1 point' means you won that trial, and a "
    "red sad face with '-1 point' means you lost that trial. To move to the next "
    "trial, press the up key after a win and the down key after a loss. "
    "You will do two sessions of 100 trials each. In each session the symbols come "
    "in two fixed pairs, and each pair is shown 50 times in a random order.\n"
    "After the two sessions comes a transfer phase. The eight symbols you saw are "
    "now shown to you two at a time, in all pairings, including ones you have not "
    "seen together before. For each pair, pick the symbol you think is the more "
    "rewarding one, and use your instinct if you are unsure. In the transfer phase "
    "you receive no feedback at all.\n"
)

TRANSFER_BEGIN = (
    "Now the transfer phase begins. The eight symbols are shown "
    "in pairs and you pick the one you think is more rewarding. "
    "No feedback is given."
)


class ContextualBandit:
    """Contextual two-armed bandit, Experiment 1 of Vandendriessche et al. (2023),
    "Contextual influence of reinforcement learning performance of depression:
    evidence for a negativity bias?", Psychological Medicine, 53(10), 4696-4706.

    Design (Methods/Procedure, pp. 4699-4700 of the paper): each participant plays a
    two-armed bandit over 8 abstract symbols in a learning phase of 2 sessions x 100
    trials (each session 50 'rich' + 50 'poor' contexts, shuffled) with binary +/-1
    feedback, followed by a no-feedback 112-trial transfer phase pairing the 8
    symbols in all binary combinations. The paper assigns reward probabilities of
    10%/40% to the two poor-context symbols and 60%/90% to the two rich-context
    symbols (such that the EV difference between the two options is 30 points in
    both contexts); the better symbol is the 90% one in the rich context and the 40%
    one in the poor context.

    The per-participant A/B letter-to-key mapping is randomized exactly as in
    build_jsonl.py (seeded by int(participant_id)). Transfer symbol pairing is
    randomized per participant: all 28 unordered pairs are shown 4 times (= each
    ordered pair twice), giving 112 trials.

    Symbol ids as in exp0.csv (transform.py): poor pair (1, 2) in session 1 and
    (5, 6) in session 2, rich pair (3, 4) / (7, 8), the odd id is the better one;
    every learning line names the two symbols and their sides. The better symbol
    is on the left on exactly 25 of the 50 trials of each context and session, as
    in the data, in a random order.
    ASSUMPTION: learning trial order within a session (the shuffled rich/poor
    sequence) is randomized per participant; build_jsonl.py sorts only by `trial`.

    The DataFrame matches exp0.csv minus the un-generatable timing/duplicate
    columns (rt, rt2, checktime, checktime2, time, subject_number, session_number,
    trial_raw, choice_raw).
    """

    def __init__(self):
        self.name = "vandendriessche_2022_contextual_exp0"
        self.num_sessions = 2
        self.trials_per_session = 100
        self.p_better = {"rich": 0.90, "poor": 0.40}
        self.p_worse = {"rich": 0.60, "poor": 0.10}
        self.num_symbols = 8
        # transfer: all binary unordered pairs, each shown 4 times = 112 trials
        pairs = list(itertools.combinations(range(1, 9), 2))
        self.transfer_pairs = pairs * 2 + [(b, a) for a, b in pairs] * 2

    def _letters(self, participant_id):
        rng = random.Random(int(participant_id))
        left, right = ("A", "B") if rng.random() < 0.5 else ("B", "A")
        return left, right

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            left, right = self._letters(participant)
            prompt = INSTRUCTIONS.format(left=left, right=right)
            trial = stopped = 0
            # learning phase: 2 sessions x 100 trials (50 rich + 50 poor)
            for session in range(1, self.num_sessions + 1):
                if stopped:
                    break
                contexts = ["rich"] * 50 + ["poor"] * 50
                rng = random.Random()
                rng.shuffle(contexts)
                # symbol ids of the session's pairs (odd = better) and the better symbol's side:
                # 25 left + 25 right per context, shuffled
                better_id = {"poor": 4 * (session - 1) + 1, "rich": 4 * (session - 1) + 3}
                better_left = {c: [True] * 25 + [False] * 25 for c in ("rich", "poor")}
                for c in better_left:
                    rng.shuffle(better_left[c])
                shown = {"rich": 0, "poor": 0}
                for t_in_s, context in enumerate(contexts):
                    if max_chars is not None and len(prompt) >= max_chars:
                        stopped = 1
                        break
                    b = better_id[context]
                    sl, sr = (b, b + 1) if better_left[context][shown[context]] else (b + 1, b)
                    shown[context] += 1
                    prompt += (f"\nOptions: symbol {sl} (left), symbol {sr} (right). "
                               f"You press [HUMAN_RESPONSE]")
                    letter = agent(prompt, choice_options=[left, right])
                    prompt += f"{letter}[/HUMAN_RESPONSE]"
                    response = 0 if letter == left else 1
                    chosen_sym = sl if response == 0 else sr
                    got_better = chosen_sym == b
                    p = (self.p_better[context] if got_better
                         else self.p_worse[context])
                    reward = 1 if rng.random() < p else 0
                    outcome = ("+1 point (green smiley)" if reward == 1
                               else "-1 point (red sad face)")
                    prompt += (f" ({'left' if response == 0 else 'right'}: symbol {chosen_sym}). "
                               f"You get {outcome}.")
                    rows.append({
                        "participant_id": participant, "group": "", "phase": "learning",
                        "trial": trial, "session": f"session{session}",
                        "context": context, "context_code": 1 if context == "poor" else 2,
                        "response": response, "correct": int(got_better), "reward": reward,
                        "trial_in_session": t_in_s, "trial_in_transfer": np.nan,
                        "symbol_left": sl, "symbol_right": sr,
                    })
                    trial += 1
            if stopped:
                prompts.append(prompt)
                continue
            prompt += "\n" + TRANSFER_BEGIN
            rng = random.Random()
            pairs = self.transfer_pairs[:]
            rng.shuffle(pairs)
            for i_tr, (sl, sr) in enumerate(pairs):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                prompt += (f"\nTransfer. Options: symbol {sl} (left), symbol {sr} (right). "
                           f"You press [HUMAN_RESPONSE]")
                letter = agent(prompt, choice_options=[left, right])
                prompt += f"{letter}[/HUMAN_RESPONSE]"
                response = 0 if letter == left else 1
                chosen_sym = sl if response == 0 else sr
                prompt += f" ({'left' if response == 0 else 'right'}: symbol {chosen_sym})."
                rows.append({
                    "participant_id": participant, "group": "", "phase": "transfer",
                    "trial": trial, "session": np.nan, "context": np.nan,
                    "context_code": np.nan, "response": response, "correct": np.nan,
                    "reward": np.nan, "trial_in_session": np.nan,
                    "trial_in_transfer": i_tr, "symbol_left": sl, "symbol_right": sr,
                })
                trial += 1
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "group", "phase", "trial", "session", "context",
            "context_code", "response", "correct", "reward", "trial_in_session",
            "trial_in_transfer", "symbol_left", "symbol_right",
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

    task = ContextualBandit()
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