# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/suthaharan_2021_paranoia`` — the
non-social probabilistic reversal-learning (card-deck) task — format-identical
to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (NONSOCIAL_INTRO / transcribe_non_social).
INSTRUCTIONS = (
    "You will play a card game. Three decks of cards are in front of you: deck A, deck B, "
    "and deck C. Each deck holds a mix of winning and losing cards - winning cards add 100 "
    "points, losing cards take away 50 points. Your job is to find the best deck and earn "
    "as many points as possible. The best deck can change, so keep testing your choices. "
    "On each trial, type A, B, or C to pick the deck you want to draw from.\n"
)

OPTIONS = ["A", "B", "C"]


class AversiveReversalLearningCard:
    """Non-social 3-option probabilistic reversal learning task, exp0 of
    Suthaharan et al. (2021), "Paranoia and belief updating during the COVID-19
    crisis", Nature Human Behaviour 5, 1190-1202.

    Design (Methods, "Behavioural tasks", p. 1200): 160 trials split into two
    80-trial halves; on each trial the participant picks one of three decks
    (A/B/C) and receives +100 points (reward=1) or loses 50 points (reward=0).
    The three decks carry reward contingencies that "began as 90% reward, 50%
    reward and 10% reward" (best/middle/worst deck) and "at the end of the
    second block" (trial 81 onwards) "transitioned to 80% reward, 40% reward
    and 20% reward", with "the allocation across deck/partner switching after
    9 out of 10 consecutive rewards".

    ASSUMPTION: the paper fixes the reward schedule (90/50/10 in block 0 then
    80/40/20 in block 1) and the 9-of-10 reversal trigger, but not the initial
    best deck nor the rotation order. Matching this repo's js-port
    (experiments/exp0), the best deck starts at A and rotates A->B->C->A after
    a sliding window of the last 10 trials spent on the best deck contains 9
    wins. Deck labels A/B/C double as the response tokens; the mapping is
    fixed (A=deck A) exactly as in build_jsonl.py.

    The DataFrame mirrors exp0.csv's trial-level columns (participant_id,
    trial, block, response, reward, phase, task_type); participant-constant
    columns (demographics, questionnaires, cohort labels, HGF parameters,
    rt/derived measures) cannot be produced by a text simulator and are
    dropped.
    """

    def __init__(self):
        self.name = "suthaharan_2021_paranoia_exp0"
        self.num_blocks = 2          # two 80-trial halves
        self.trials_per_block = 80   # 160 trials total
        self.window = 10             # sliding 9-of-10 reversal window
        self.reversal_threshold = 9
        self.schedule = {
            0: np.array([0.9, 0.5, 0.1]),   # best / middle / worst, block 0
            1: np.array([0.8, 0.4, 0.2]),   # best / middle / worst, block 1
        }

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            pid = f"P{participant:03d}"
            prompt = INSTRUCTIONS
            # contingencies are fixed per block, best deck starts at A (=0) and
            # rotates A->B->C after 9-of-10 wins observed on the current best.
            best = 0
            best_window = []
            for block in range(self.num_blocks):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                probs = self.schedule[block]
                for trial in range(self.trials_per_block):
                    prompt += "You draw a card from deck [HUMAN_RESPONSE]"
                    letter = agent(prompt, choice_options=OPTIONS)
                    response = OPTIONS.index(letter)
                    reward = int(np.random.rand() < probs[(response - best) % 3])  # best/middle/worst relative to `best`
                    prompt += (
                        f"{letter}[/HUMAN_RESPONSE]. "
                        f"{'You won 100 points.' if reward else 'You lost 50 points.'}\n"
                    )
                    rows.append({
                        "participant_id": pid,
                        "trial": block * self.trials_per_block + trial,
                        "block": block,
                        "response": response,
                        "reward": reward,
                        "phase": "test",
                        "task_type": "nonsocial",
                    })
                    if response == best:
                        best_window.append(reward)
                        if len(best_window) > self.window:
                            best_window.pop(0)
                        if (len(best_window) == self.window
                                and sum(best_window) >= self.reversal_threshold):
                            best = (best + 1) % 3
                            best_window = []
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "block", "response", "reward", "phase", "task_type",
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

    task = AversiveReversalLearningCard()
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