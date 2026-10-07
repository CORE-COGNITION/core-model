# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/russek_2024_heuristics``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (EXP0_INSTR).
INSTRUCTIONS = (
    "You are taking part in a risky decision-making task. On each trial you are offered a "
    "gamble and you must decide whether to accept it or reject it. The gamble has two possible "
    "outcomes, O1 and O2: if you accept the gamble, you receive one of them by chance. If you "
    "reject it, you instead collect a fixed safe outcome. First, three banknote images appear, "
    "each showing the number of points its outcome is worth: O1, O2, and the safe option. Then a "
    "probability symbol appears showing how likely you are to get O1 if you accept the gamble. "
    "Press A to accept the gamble, or press R to reject it and take the safe outcome. Your bonus "
    "is based on the points you collect. On gain blocks the points are positive; on loss blocks "
    "the points are negative (losses)."
)

_TRIGGER = {"gain": [47.5, 60.0, 75.0], "loss": [-47.5, -60.0, -75.0]}
_SAFE = {"gain": [20, 32, 44, 56], "loss": [-20, -32, -44, -56]}
_PROB = [0.2, 0.4, 0.6, 0.8]


def _fmt(v):
    v = float(v)
    return str(int(v)) if v == int(v) else f"{v:.1f}"


def _prob(p):
    return f"{round(float(p) * 100)}%"


class MEGRiskyDecision:
    """Risky decision-making task, Experiment 1 (MEG) of Russek et al. (2024),
    "Heuristics in risky decision-making relate to preferential representation of
    information", Nature Communications 15, 4269. exp0 of the dataset (N=21).

    Design (Methods "Risky decision-making task", p. 10-11; Fig. 1): 8 blocks
    alternating gain and loss (four of each). Each trial, O1 or O2 is the
    "trigger" outcome; its base value is drawn from {47.5, 60, 75} on gain
    blocks (negated on loss blocks) and the non-trigger outcome is 0; the safe
    option's base value is drawn from {20, 32, 44, 56} (negated on loss blocks)
    with the constraint that |trigger| > |safe|. A common noise U(0,20) (gain)
    / U(-20,0) (loss) is added to all three outcomes, then each outcome gets its
    own U(0,5) (gain) / U(-5,0) (loss) noise. The probability that O1 is
    encountered if the gamble is accepted is p in {0.2, 0.4, 0.6, 0.8}; the
    trigger outcome's probability p_trigger is equal to p_o1 when O1 is the
    trigger and 1 - p_o1 otherwise. Participants decide accept (A) or reject (R);
    accepting pays O1/O2 with probability p_o1, rejecting pays the safe outcome.

    ASSUMPTION: each block is simulated with 36 trials (the observed data has
    33-36; the paper only fixes the total of 8 alternating blocks).
    ASSUMPTION: the block type ordering is random per participant (gain- or
    loss-first), matching the two orderings present in exp0.csv.

    The DataFrame matches exp0.csv minus ``rt``, ``rt_sec``, ``choice_number``
    and ``trial_number`` (timing / source bookkeeping a text simulator cannot
    produce); ``phase`` is kept as the constant "test".
    """

    def __init__(self):
        self.name = "russek_2024_heuristics_exp0"
        self.num_blocks = 8
        self.trials_per_block = 36

    def _draw_trial(self, gl_type):
        trigger_base = float(np.random.choice(_TRIGGER[gl_type]))
        safe_base = float(np.random.choice([s for s in _SAFE[gl_type] if abs(s) < abs(trigger_base)]))
        o1_trigger = int(np.random.choice([0, 1]))
        p_trigger = float(np.random.choice(_PROB))
        p_o1 = p_trigger if o1_trigger == 1 else 1.0 - p_trigger
        if gl_type == "gain":
            common = np.random.uniform(0, 20)
            n_trig, n_other, n_safe = np.random.uniform(0, 5, size=3)
        else:
            common = np.random.uniform(-20, 0)
            n_trig, n_other, n_safe = np.random.uniform(-5, 0, size=3)
        trigger_actual = trigger_base + common + n_trig
        other_noise = common + n_other
        safe_actual = safe_base + common + n_safe
        o1_val = round(trigger_actual) if o1_trigger == 1 else round(other_noise)
        o2_val = round(trigger_actual) if o1_trigger == 0 else round(other_noise)
        safe_val = round(safe_actual)
        return {
            "trigger_val_base": trigger_base, "trigger_val_actual": trigger_actual,
            "safe_val_base": safe_base, "safe_val_actual": float(safe_val),
            "other_noise": other_noise, "o1_trigger": o1_trigger,
            "p_trigger": p_trigger, "p_o1": p_o1,
            "o1_val": float(o1_val), "o2_val": float(o2_val), "safe_val": float(safe_val),
        }

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            start = "gain" if np.random.rand() < 0.5 else "loss"
            order = [start if b % 2 == 0 else ("loss" if start == "gain" else "gain")
                     for b in range(self.num_blocks)]
            prompt = INSTRUCTIONS + "\n"
            for block in range(self.num_blocks):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                gl_type = order[block]
                for trial in range(self.trials_per_block):
                    t = self._draw_trial(gl_type)
                    o1, o2, safe = _fmt(t["o1_val"]), _fmt(t["o2_val"]), _fmt(t["safe_val"])
                    p1, p2 = _prob(t["p_o1"]), _prob(1.0 - t["p_o1"])
                    cue = (f"({gl_type} block) O1 is worth {o1} points, O2 is worth {o2} points, "
                           f"the safe option is worth {safe} points. "
                           f"If you accept, you have a {p1} chance of O1 and a {p2} chance of O2. "
                           f"You press [HUMAN_RESPONSE]")
                    prompt += cue
                    letter = agent(prompt, choice_options=["A", "R"])
                    response = 1 if letter == "A" else 0
                    if response == 1:
                        outcome_reached = 1.0 if np.random.rand() < t["p_o1"] else 2.0
                        out_val = t["o1_val"] if outcome_reached == 1 else t["o2_val"]
                        prompt += (f"A[/HUMAN_RESPONSE]. You receive the "
                                   f"O{int(outcome_reached)} outcome ({_fmt(out_val)} points).")
                    else:
                        outcome_reached = 3.0
                        prompt += (f"R[/HUMAN_RESPONSE]. You reject the gamble and receive "
                                   f"the safe outcome ({safe} points).")
                    prompt += "\n"
                    rows.append({
                        "participant_id": participant, "trial": trial + block * self.trials_per_block,
                        "response": response, "block_number": block + 8,
                        "safe_val_actual": t["safe_val_actual"], "safe_val_base": t["safe_val_base"],
                        "trigger_val_actual": t["trigger_val_actual"],
                        "trigger_val_base": t["trigger_val_base"],
                        "other_noise": t["other_noise"], "o1_trigger": t["o1_trigger"],
                        "gl_type": gl_type, "accept": response, "phase": "test",
                        "p_trigger": t["p_trigger"], "p_o1": t["p_o1"],
                        "o1_val": t["o1_val"], "o2_val": t["o2_val"], "safe_val": t["safe_val"],
                        "outcome_reached": outcome_reached, "task_block_number": block + 1,
                        "gain_trial": int(gl_type == "gain"), "loss_trial": int(gl_type == "loss"),
                        "block": block,
                    })
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "block_number",
            "safe_val_actual", "safe_val_base", "trigger_val_actual", "trigger_val_base",
            "other_noise", "o1_trigger", "gl_type", "accept", "phase",
            "p_trigger", "p_o1", "o1_val", "o2_val", "safe_val", "outcome_reached",
            "task_block_number", "gain_trial", "loss_trial", "block",
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

    task = MEGRiskyDecision()
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
