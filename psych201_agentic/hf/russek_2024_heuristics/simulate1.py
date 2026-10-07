# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 of ``Hugging-Brain/russek_2024_heuristics``,
format-identical to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (EXP1_INSTR).
INSTRUCTIONS = (
    "You are taking part in a risky decision-making task. On each trial you first see three "
    "banknote images, each showing the number of points its outcome is worth: O1, O2, and a safe "
    "option. Then a probability symbol appears showing how likely you are to get O1 if you accept "
    "the gamble. On most trials you then decide whether to accept the gamble or reject it (and "
    "take the safe outcome): press A to accept, or press R to reject. On some trials, instead of "
    "choosing, the three outcome images appear and an arrow sits over one of them; press the arrow "
    "key matching the arrow's direction as quickly as you can. Your arrow report is recorded as "
    "either correct or incorrect. On gain blocks the points are positive; on loss blocks the "
    "points are negative (losses)."
)

_TRIGGER = {"gain": [47.5, 60.0, 75.0], "loss": [-47.5, -60.0, -75.0]}
_SAFE = {"gain": [20, 32, 44, 56], "loss": [-20, -32, -44, -56]}
_PROB = [0.2, 0.4, 0.6, 0.8]
_IMAGES = ["Stimuli/Evan_Stimuli/Scissors.png", "Stimuli/Evan_Stimuli/Girl.png",
           "Stimuli/Evan_Stimuli/House.png"]


def _fmt(v):
    v = float(v)
    return str(int(v)) if v == int(v) else f"{v:.1f}"


def _prob(p):
    return f"{round(float(p) * 100)}%"


class PerceptualDetection:
    """Perceptual detection / recognition task, Experiment 2 of Russek et al.
    (2024), "Heuristics in risky decision-making relate to preferential
    representation of information", Nature Communications 15, 4269. exp1 of the
    dataset (N=97).

    Design (Methods "Perceptual detection task procedures", p. 14; Main text
    "Perceptual detection task"; Fig. 6A): 4 blocks (block 0..3, ~72 trials
    each, 288 trials total) alternating gain/loss. Two thirds of trials are
    accept/reject choice trials identical to the MEG risky-decision task: O1 or
    O2 is the trigger (base {47.5, 60, 75} gain / negated on loss, non-trigger
    0), the safe option is drawn from {20, 32, 44, 56} (negated on loss) with
    |trigger| > |safe|, common noise U(0,20)/U(-20,0) plus per-outcome
    U(0,5)/U(-5,0) noise, and p(O1) drawn from {0.2, 0.4, 0.6, 0.8}. On one
    third of trials, instead of choosing, the probability stimulus disappears
    and the three outcome stimuli are shown with an arrow over one of them
    (recognition_number: 1/2/3 = O1/O2/safe image); participants press the
    arrow key as fast as they can. The source records only whether that
    report was correct (`correct`), so the agent is not queried on detection
    trials: the outcome is drawn and narrated as plain text.

    ASSUMPTION: condition (choice vs detection) is assigned per trial with
    P(detection) = 1/3, the observed ratio; recognition_number is uniform over
    {1,2,3} and stim_pos_y uniform over {1,2}.
    ASSUMPTION: the arrow report is correct with P = 0.928 (the observed
    rate) on detection trials that get a response.
    ASSUMPTION: on a small fraction of trials (observed ~0.8% of choice,
    ~7.7% of detection) the participant fails to respond in time (valid=0,
    response NaN) and the trial is narrated "You fail to respond in time.".
    ASSUMPTION: the three outcome images (Scissors/Girl/House) are assigned to
    O1/O2/safe per participant as a fixed random permutation; the filenames are
    metadata only (build_jsonl narrates only the "O1/O2/safe image" labels).

    The DataFrame matches exp1.csv minus ``rt``, ``rt_sec``, ``choice_number``
    and ``trial_number`` (timing / source bookkeeping a text simulator cannot
    produce); ``phase`` is kept as the constant "test".
    """

    def __init__(self):
        self.name = "russek_2024_heuristics_exp1"
        self.num_blocks = 4
        self.trials_per_block = 72
        self.p_detection = 1.0 / 3.0
        self.p_miss_choice = 0.008
        self.p_miss_detection = 0.077
        self.p_correct_detection = 0.928

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
            perm = np.random.permutation(_IMAGES)
            images = {"o1": perm[0], "o2": perm[1], "safe": perm[2]}
            prompt = INSTRUCTIONS + "\n"
            for block in range(self.num_blocks):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                gl_type = order[block]
                for trial in range(self.trials_per_block):
                    t = self._draw_trial(gl_type)
                    o1, o2, safe = _fmt(t["o1_val"]), _fmt(t["o2_val"]), _fmt(t["safe_val"])
                    p1, p2 = _prob(t["p_o1"]), _prob(1.0 - t["p_o1"])
                    is_detection = np.random.rand() < self.p_detection
                    if not is_detection:
                        p_miss = self.p_miss_choice
                    else:
                        p_miss = self.p_miss_detection
                    missed = np.random.rand() < p_miss

                    if not is_detection:
                        cue = (f"({gl_type} block) O1 is worth {o1} points, O2 is worth {o2} "
                               f"points, the safe option is worth {safe} points. "
                               f"If you accept, you have a {p1} chance of O1 and a {p2} chance "
                               f"of O2. ")
                        if missed:
                            prompt += cue + "You fail to respond in time.\n"
                            rows.append(self._choice_row(participant, trial, block, gl_type, t,
                                                         images, response=None, valid=0,
                                                         stim_pos_y=np.random.choice([1, 2])))
                            continue
                        prompt += cue + "You press [HUMAN_RESPONSE]"
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
                        rows.append(self._choice_row(participant, trial, block, gl_type, t,
                                                     images, response=response, valid=1,
                                                     outcome_reached=outcome_reached,
                                                     stim_pos_y=np.random.choice([1, 2])))
                    else:
                        recognition_number = float(np.random.choice([1, 2, 3]))
                        if recognition_number == 1:
                            stim = "O1 image"
                        elif recognition_number == 2:
                            stim = "O2 image"
                        else:
                            stim = "safe image"
                        pos = int(np.random.choice([1, 2]))
                        stim_pos_y = float(pos)
                        cue = (f"O1 is worth {o1} points, O2 is worth {o2} points, the safe "
                               f"option is worth {safe} points. "
                               f"If you accept, you have a {p1} chance of O1. "
                               f"An arrow appears over the {stim} (vertical position {pos}). ")
                        if missed:
                            prompt += cue + "You fail to respond in time.\n"
                            rows.append(self._detection_row(participant, trial, block, gl_type, t,
                                                            recognition_number, stim_pos_y,
                                                            images, correct=None, valid=0))
                            continue
                        correct = 1 if np.random.rand() < self.p_correct_detection else 0
                        prompt += cue + f"Your arrow report is {'correct' if correct else 'incorrect'}."
                        prompt += "\n"
                        rows.append(self._detection_row(participant, trial, block, gl_type, t,
                                                        recognition_number, stim_pos_y,
                                                        images, correct=correct, valid=1))
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "block_number",
            "safe_val_actual", "safe_val_base", "trigger_val_actual", "trigger_val_base",
            "other_noise", "o1_trigger", "gl_type", "accept", "phase",
            "p_trigger", "p_o1", "o1_val", "o2_val", "safe_val", "outcome_reached",
            "recognition_number", "correct_recognition", "o1_image", "o2_image",
            "safe_image", "stim_pos_y", "block", "condition", "correct", "valid",
        ])
        return df, prompts

    def _choice_row(self, participant, trial, block, gl_type, t, images, response, valid,
                    outcome_reached=None, stim_pos_y=1):
        base = {
            "participant_id": participant, "trial": trial + block * self.trials_per_block,
            "block_number": block + 8, "safe_val_actual": t["safe_val_actual"],
            "safe_val_base": t["safe_val_base"], "trigger_val_actual": t["trigger_val_actual"],
            "trigger_val_base": t["trigger_val_base"], "other_noise": t["other_noise"],
            "o1_trigger": t["o1_trigger"], "gl_type": gl_type, "phase": "test",
            "p_trigger": t["p_trigger"], "p_o1": t["p_o1"],
            "o1_val": t["o1_val"], "o2_val": t["o2_val"], "safe_val": t["safe_val"],
            "o1_image": images["o1"], "o2_image": images["o2"], "safe_image": images["safe"],
            "stim_pos_y": float(stim_pos_y), "condition": "choice", "valid": valid,
            "correct": np.nan, "block": block,
        }
        if response is None:
            base.update({"response": np.nan, "accept": np.nan,
                         "outcome_reached": np.nan, "recognition_number": 0.0,
                         "correct_recognition": np.nan})
        else:
            base.update({"response": float(response), "accept": float(response),
                         "outcome_reached": outcome_reached, "recognition_number": 0.0,
                         "correct_recognition": np.nan})
        return base

    def _detection_row(self, participant, trial, block, gl_type, t, recognition_number,
                       stim_pos_y, images, correct, valid):
        base = {
            "participant_id": participant, "trial": trial + block * self.trials_per_block,
            "block_number": block + 8, "safe_val_actual": t["safe_val_actual"],
            "safe_val_base": t["safe_val_base"], "trigger_val_actual": t["trigger_val_actual"],
            "trigger_val_base": t["trigger_val_base"], "other_noise": t["other_noise"],
            "o1_trigger": t["o1_trigger"], "gl_type": gl_type, "phase": "test",
            "p_trigger": t["p_trigger"], "p_o1": t["p_o1"],
            "o1_val": t["o1_val"], "o2_val": t["o2_val"], "safe_val": t["safe_val"],
            "response": np.nan, "accept": np.nan, "outcome_reached": np.nan,
            "recognition_number": recognition_number, "stim_pos_y": stim_pos_y,
            "condition": "detection", "valid": valid,
            "o1_image": images["o1"], "o2_image": images["o2"], "safe_image": images["safe"],
            "block": block,
        }
        if correct is None:
            base.update({"correct": np.nan, "correct_recognition": np.nan})
        else:
            base.update({"correct": float(correct), "correct_recognition": float(correct)})
        return base


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

    task = PerceptualDetection()
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