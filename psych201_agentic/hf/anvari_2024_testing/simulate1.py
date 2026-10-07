# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for the sampling paradigm, exp1 of ``Hugging-Brain/anvari_2024_testing``,
format-identical to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import random

import numpy as np
import pandas as pd
from tqdm import tqdm

PAPER = "Hugging-Brain/anvari_2024_testing"

INSTRUCTIONS = (
    "You see two buttons, each with an unknown chance of paying a fixed number of "
    "points. You can sample the buttons as many times as you like (up to 100 per "
    "block) to learn what they pay; each sample shows what that button would have "
    "paid. You must sample each button at least once. When you stop sampling you "
    "choose which button to be paid out from, and it pays once more. For each point "
    "you earn a bonus of 5p. Press {s1} to sample Button 1, {s2} to sample Button 2, "
    "{c1} to stop and be paid from Button 1, or {c2} to stop and be paid from Button 2.")

# the study's six option pairs ("<points>_<probability>"), pair id = player_presentation_order
PAIRS = {
    1: ("1_1.0", "10_0.1"),      # practice
    2: ("3_1.0", "4_0.8"),
    3: ("3_1.0", "16_0.2"),
    4: ("3_0.25", "4_0.2"),
    5: ("3_1.0", "32_0.1"),
    6: ("9_1.0", "10_0.9"),
}


def _shuffled_letters(pid, letters):
    rnd = random.Random(f"{PAPER}:{pid}")
    ls = list(letters)
    rnd.shuffle(ls)
    return ls


def _fmt(x):
    return f"{x:g}" if isinstance(x, (int, float)) else str(x)


class SamplingParadigm:
    """Sampling paradigm, exp1 of Anvari et al. (2024), Nature Communications 15, 7721.

    Design (Methods, "Sampling paradigm", p. 15): two buttons each with an unknown
    probability of paying a fixed number of points (or zero). Participants sample
    as often as they like (each button at least once, at most 100 samples per
    block), then choose a button to be paid from; that button pays once more.
    1 practice block + 5 incentivized blocks. The option strings carry the fixed
    payoff and its probability ("<value>_<prob>").

    ASSUMPTION: the six option pairs and their ids come from the shipped data (the
    paper lists them in its Supplemental Information); the five incentivized pairs
    are played in random order and each pair's left/right position is random, as
    in the data. response codes the four actions: 0/1 = sample Button 1/2,
    2/3 = stop and be paid from Button 1/2. Every sample and the final draw pay
    their outcome; the shipped exp1.csv has reward only on the final-choice row
    because the source does not record the outcome of the individual samples.
    """

    def __init__(self):
        self.name = "anvari_2024_testing_exp1"
        self.n_blocks = 6          # 0 = practice, 1..5 = incentivized
        self.max_samples = 100

    @staticmethod
    def _draw(opt):
        v, p = opt.split("_")
        return float(v) if np.random.rand() < float(p) else 0.0

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            pid = f"P{participant:03d}"
            s1, s2, c1, c2 = _shuffled_letters(pid, ["A", "B", "C", "D"])
            sample_btn = {s1: 1, s2: 2}
            final_btn = {c1: 1, c2: 2}
            prompt = INSTRUCTIONS.format(s1=s1, s2=s2, c1=c1, c2=c2)
            order = [1] + list(np.random.permutation([2, 3, 4, 5, 6]))
            for task_id in range(self.n_blocks):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                tag = "practice" if task_id == 0 else "incentivized"
                prompt += f"\n{tag} block begins."
                pair_id = int(order[task_id])
                opts = list(PAIRS[pair_id])
                if np.random.rand() < 0.5:
                    opts.reverse()
                opt1, opt2 = opts
                counts = {1: 0, 2: 0}
                trial = 0
                block_rows = []
                while True:
                    options = [s1, s2] if trial < self.max_samples else []
                    if counts[1] > 0 and counts[2] > 0:
                        options += [c1, c2]
                    prompt += "\nYou press [HUMAN_RESPONSE]"
                    letter = agent(prompt, choice_options=options)
                    if letter in sample_btn:
                        btn = sample_btn[letter]
                        pay = self._draw(opt1 if btn == 1 else opt2)
                        counts[btn] += 1
                        prompt += (f"{letter}[/HUMAN_RESPONSE] and sample Button {btn}; "
                                   f"it pays {_fmt(pay)} points.")
                        final = 0
                    else:
                        btn = final_btn[letter]
                        pay = self._draw(opt1 if btn == 1 else opt2)
                        prompt += (f"{letter}[/HUMAN_RESPONSE] and choose to be paid from "
                                   f"Button {btn}; it pays {_fmt(pay)} points.")
                        final = 1
                    block_rows.append({
                        "participant_id": pid, "session": "time1",
                        "task_id": task_id, "trial": trial,
                        "response": btn - 1 + 2 * final,
                        "phase": "practice" if task_id == 0 else "test",
                        "player_selection": None if final else btn,
                        "player_option_1_probability": opt1,
                        "player_option_2_probability": opt2,
                        "player_presentation_order": pair_id,
                        "reward": pay,
                        "final_choice": final,
                    })
                    trial += 1
                    if final:
                        break
                for r in block_rows:
                    r["player_sampling_option"] = btn
                    r["player_sampler_payoff"] = pay
                    r["player_final_choice"] = opt1 if btn == 1 else opt2
                rows.extend(block_rows)
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "session", "task_id", "trial", "response", "phase",
            "player_sampling_option", "player_sampler_payoff", "player_selection",
            "player_option_1_probability", "player_option_2_probability",
            "player_final_choice", "player_presentation_order", "reward", "final_choice",
        ])
        df["player_selection"] = df["player_selection"].astype("Int64")
        return df, prompts


class _RandomAgent:
    def __init__(self):
        self.rng = np.random.default_rng()

    def __call__(self, prompt, choice_options):
        return str(self.rng.choice(list(choice_options)))


def main():
    parser = argparse.ArgumentParser(
        description="Smoke-test this simulator with a uniform-random agent.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3)
    parser.add_argument("--max-chars", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)
        random.seed(args.seed)

    task = SamplingParadigm()
    df, prompts = task.simulate(_RandomAgent(), args.num_simulations,
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
    print(prompts[0][:400])
    print("...")
    print("first prompt, tail:")
    print(prompts[0][-250:])


if __name__ == "__main__":
    main()
