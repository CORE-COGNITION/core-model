# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/xu_2023_augmenting``, format-identical
to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp0).
INSTRUCTIONS = (
    "You take part in a study on math problem solving. For each question you will "
    "see a congruence statement of the form \"AB \u2261 CD (mod E)\", where AB and CD "
    "are two two-digit numbers and E is a one-digit number. To answer, first subtract "
    "CD from AB, then judge whether the result is divisible by E. If it is, the "
    "statement is true; otherwise it is false. Take accuracy as your first priority, "
    "then answer as quickly as you can. You answer by pressing the button for True or "
    "False: press T for True, press F for False.\n"
    "In some blocks a progress bar may appear at the top of the screen while you are "
    "answering. It fills by one unit per second and resets after 5 seconds. It is only "
    "there to convey a sense of passing time; there is no penalty associated with it.\n"
    "First you complete a practice block to get familiar with the task. Then you "
    "complete two main blocks of 100 questions each. After each main block you will be "
    "asked to rate your current attention level and your current anxiety level, each on "
    "a scale from 1 to 7 (1 = lowest, 7 = highest); to answer, type a single number "
    "from 1 to 7."
)

PRACTICE_VALUES = list(range(1, 11))
PRACTICE_WEIGHTS = [2, 2, 2, 3, 2, 4, 2, 12, 16, 34]  # empirical counts over 79 participants


class ModularArithmetic:
    """Modular-arithmetic verification task, the single experiment of Xu & Zhang
    (2023), "Augmenting Human Cognition with an AI-Mediated Intelligent Visual
    Feedback", CHI '23, https://doi.org/10.1145/3544548.3580905.

    Design (Section 3 Cognition Task; Section 6.3 Study Procedure; Section 6.4
    Experimental Design): each trial shows a congruence "AB \u2261 CD (mod E)".
    The participant subtracts CD from AB and decides whether the result is
    divisible by E, pressing a True/False button (a free binary response). Each
    participant does a variable-length practice block, then two counterbalanced
    blocks of 100 test trials each: a Control block (no time pressure) and a
    Feedback block (a visual progress bar may appear above the problem, chosen
    per trial by the feedback strategy). After each formal block the participant
    rates their current attention and anxiety on 1-7 Likert scales (free
    self-reports). Response tokens are fixed: T = True, F = False, and single
    digits 1-7 for the ratings.

    Stimulus generation follows the shipped js experiment and the data: AB is a
    two-digit number 21-99, CD a two-digit number 11-89 with CD < AB, E in 3-9;
    the ground truth (AB-CD) % E == 0 is balanced to ~50% true/false.

    Feedback strategy per group (Section 6.4): the Random group gets a 50% coin
    per trial in the Feedback block (matches the data ~0.50); the RL group gets
    adaptive time pressure from a trained PPO regulation agent whose weights are
    not published, so a documented heuristic on the same observation is used
    (running-mean RT + last-10 RT buffer; show the bar when the recent run is
    slower than the running mean), matching the shipped js experiment.

    ASSUMPTION (practice length): the paper describes two 10-trial practice
    sessions (up to 20 trials), but exp0.csv records a single variable-length
    practice session (1-10 trials). Per the data-authoritative rule the
    simulator samples the practice length from the data's empirical distribution.

    ASSUMPTION (RL feedback): the RL group's Feedback block is driven by a
    trained PPO agent whose weights are unpublished. Substituted with the
    documented RT-based heuristic (same observation) used by the shipped js
    experiment; this affects only which experimenter-controlled trials show the
    progress bar, never the participant response format.

    ASSUMPTION (feedback fraction): per the data the Feedback block shows the
    bar on ~45-50% of trials (Random ~0.50, RL ~0.45). The simulator follows the
    paper's 50% coin for Random and the heuristic for RL.

    ASSUMPTION (dropped columns): rt, attentiontime and anxietytime are response
    times a text simulator cannot produce and are dropped. A synthetic RT is
    drawn internally (only to drive the RL feedback heuristic) and not emitted.

    The DataFrame matches exp0.csv minus ``rt``, ``attentiontime``, ``anxietytime``.
    """

    def __init__(self):
        self.name = "xu_2023_augmenting_exp0"
        self.num_block_trials = 100
        self.rt_mean = 5000.0
        self.rt_sd = 2000.0
        self.rating_options = [str(i) for i in range(1, 8)]

    def _draw_stimulus(self):
        n1 = int(np.random.randint(2, 10)) * 10 + int(np.random.randint(1, 10))
        n2 = int(np.random.randint(1, n1 // 10)) * 10 + int(np.random.randint(1, 10))
        n3 = int(np.random.randint(3, 10))
        target = int(np.random.randint(0, 2))
        while ((n1 - n2) % n3 == 0) != bool(target):
            n1 = int(np.random.randint(2, 10)) * 10 + int(np.random.randint(1, 10))
            n2 = int(np.random.randint(1, n1 // 10)) * 10 + int(np.random.randint(1, 10))
            n3 = int(np.random.randint(3, 10))
        truth = 1 if (n1 - n2) % n3 == 0 else 0
        stimulus = f"{n1} \u2261 {n2} (mod {n3})"
        return stimulus, truth

    def _sample_practice(self):
        return int(np.random.choice(PRACTICE_VALUES, p=[w / 79.0 for w in PRACTICE_WEIGHTS]))

    def simulate(self, agent, num_simulations, max_chars=None):
        all_rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            rows = []
            condition = "rl" if np.random.rand() < 0.5 else "random"
            order = 0 if np.random.rand() < 0.5 else 1
            # block ordering: practice, then task0 (first), then task1
            # order==0 -> task0 control, task1 feedback ; order==1 -> task0 feedback, task1 control
            task0_fb = order == 1
            task1_fb = order == 0
            prompt = INSTRUCTIONS
            trial = 0
            step = 0
            prev_task = None
            blocks = [
                (-1, False, self._sample_practice()),
                (0, task0_fb, self.num_block_trials),
                (1, task1_fb, self.num_block_trials),
            ]
            for task, is_fb, count in blocks:
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                if task == 0:
                    step = 0  # exp0.csv restarts `step` at the formal session
                if prev_task is not None and task != prev_task and prev_task != -1:
                    pass  # rating line already emitted at end of the previous formal block
                if prev_task is None or task != prev_task:
                    if task == -1:
                        prompt += (f"\nThe practice block begins. You work through "
                                   f"{count} practice problems. No progress bar is shown.")
                    elif is_fb:
                        prompt += ("\nThe next block of 100 questions begins. A progress bar may "
                                   "appear above the problem while you are answering.")
                    else:
                        prompt += ("\nThe next block of 100 questions begins. No progress bar is "
                                   "shown in this block.")
                prev_task = task

                # feedback-strategy state (RL heuristic only uses it)
                buffer, overall_sum, overall_count = [], 0.0, 0

                for _ in range(count):
                    stimulus, truth = self._draw_stimulus()
                    rt_ms = float(np.clip(np.random.normal(self.rt_mean, self.rt_sd), 0.5, 30000.0))

                    if task == -1 or not is_fb:
                        fb = 0
                    elif condition == "random":
                        fb = 1 if np.random.rand() < 0.5 else 0
                    else:  # rl feedback block
                        if overall_count == 0:
                            fb = 1 if np.random.rand() < 0.5 else 0
                        else:
                            overall = overall_sum / overall_count
                            recent = (sum(buffer) / len(buffer)) if buffer else overall
                            fb = 1 if recent > overall else 0
                    if is_fb and condition == "rl":
                        rt_s = rt_ms / 1000.0
                        if 0.5 < rt_s < 30.0:
                            buffer.append(rt_s)
                            if len(buffer) > 10:
                                buffer.pop(0)
                            overall_sum += rt_s
                            overall_count += 1

                    prompt += f"\nYou see the problem: {stimulus}. You press [HUMAN_RESPONSE]"
                    letter = agent(prompt, choice_options=["T", "F"])
                    response = 1 if letter == "T" else 0
                    prompt += f"{letter}[/HUMAN_RESPONSE]."
                    if fb == 1:
                        prompt += " A progress bar appears above the problem."

                    rows.append({
                        "participant_id": participant,
                        "trial": trial,
                        "response": response,
                        "correct": int(response == truth),
                        "stimulus": stimulus,
                        "truth": truth,
                        "feedback": fb,
                        "phase": "test" if task >= 0 else "practice",
                        "session": "formal" if task >= 0 else "calib",
                        "step": step + 1,
                        "condition": condition,
                        "order": order,
                        "task": task,
                        "attention": np.nan,
                        "anxiety": np.nan,
                    })
                    trial += 1
                    step += 1

                if task != -1:
                    prompt += ("\nYou finish this block of 100 questions. You rate your current "
                               "attention level: [HUMAN_RESPONSE]")
                    attn_letter = agent(prompt, choice_options=self.rating_options)
                    prompt += f"{attn_letter}[/HUMAN_RESPONSE]. You rate your current anxiety "
                    prompt += "level: [HUMAN_RESPONSE]"
                    anx_letter = agent(prompt, choice_options=self.rating_options)
                    prompt += f"{anx_letter}[/HUMAN_RESPONSE]."
                    attn, anx = int(attn_letter), int(anx_letter)
                    for r in rows:
                        if r["task"] == task:
                            r["attention"] = float(attn)
                            r["anxiety"] = float(anx)

            prompts.append(prompt)
            all_rows.extend(rows)
        df = pd.DataFrame(all_rows, columns=[
            "participant_id", "trial", "response", "correct", "stimulus", "truth",
            "feedback", "phase", "session", "step", "condition", "order", "task",
            "attention", "anxiety",
        ])
        return df, prompts


def _random_agent(prompt, choice_options):
    return str(np.random.choice(choice_options))


def main():
    parser = argparse.ArgumentParser(
        description="Smoke-test this simulator with a uniform-random agent.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3, help="number of simulated participants (default: 3)")
    parser.add_argument("--max-chars", type=int, default=None, help="stop each participant at the block boundary at/past this many chars")
    parser.add_argument("--seed", type=int, default=None, help="numpy random seed, for reproducible runs")
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    task = ModularArithmetic()
    df, prompts = task.simulate(_random_agent, args.num_simulations, max_chars=args.max_chars)

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
            first = first[:90] + " \u2026 " + first[-90:]
        print(f"participant {i} first line: {first}")
    print("=" * 78)
    print("first prompt, head:")
    print(prompts[0][:600])
    print("...")
    print("first prompt, tail:")
    print(prompts[0][-300:])


if __name__ == "__main__":
    main()