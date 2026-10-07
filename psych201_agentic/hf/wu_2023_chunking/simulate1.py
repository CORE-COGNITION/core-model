# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 (Experiment 2: speed vs accuracy, illusory chunks) of
``Hugging-Brain/wu_2023_chunking``, format-identical to ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim narration templates from build_jsonl.py (transcribe_exp1).
PARA1 = (
    "You take part in a serial reaction time experiment. On each trial, one of the "
    "four keys D, F, J, or K is displayed as the instruction cue, and you press the "
    "corresponding key. Press D for the key labeled D, F for F, J for J, and K for "
    "K.\n")
FAST_PARA = ("During the training blocks you are instructed to respond as fast as "
             "possible even if it might lead to mistakes. Your reward depends on "
             "how fast you press the instructed key, and you get trial-by-trial "
             "feedback on your reaction times. During baseline and test blocks you "
             "act as fast and accurately as possible.\n")
ACCURATE_PARA = ("During the training blocks you are instructed to respond as "
                 "accurately as possible even if it might slow you down. Your "
                 "reward depends on your accuracy, and you get trial-by-trial "
                 "feedback on correctness. During baseline and test blocks you act "
                 "as fast and accurately as possible.\n")
SESSION_PARA = ("The session has baseline, training, and test blocks followed by a "
                "practice and an instruction (free-press) block, each with 100 "
                "trials. After each trial you see your reaction time and whether "
                "you were correct, then the next trial begins after a short "
                "interval.\n")

COND_NAME = {0: "fast", 1: "accurate"}
PHYSICAL_KEYS = ["D", "F", "J", "K"]
PHASE_BY_BLOCK = {0: "baseline", 1: "baseline", 2: "training", 3: "training",
                  4: "training", 5: "training", 6: "training", 7: "training",
                  8: "test", 9: "test", 10: "practice", 11: "instruction"}
# trialinstruction per block (data: n for baseline/test, f/a training, p practice, i instruction).
TRIALINST = {0: "n", 1: "n", 2: "f", 3: "f", 4: "f", 5: "f", 6: "f", 7: "f",
             8: "n", 9: "n", 10: "p", 11: "i"}
# Fixed free-press ("O") positions (trialcollect 1..100) in the practice block.
PRACTICE_FREE = [4, 9, 11, 15, 18, 24, 26, 31, 35, 44, 49, 52, 57, 58, 60, 66, 71,
                 72, 74, 78, 82, 85, 89, 97, 99]

# "Illusory" first-order Markov matrix over abstract indices A,B,C,D (paper Fig. 1c).
ILLUSORY_P = [
    [0.0333, 0.9,    0.0333, 0.0333],
    [0.1,    0.1,    0.7,    0.1   ],
    [0.0333, 0.0333, 0.0333, 0.9   ],
    [0.7,    0.1,    0.1,    0.1   ],
]
ILLUSORY_STATIONARY = [0.2307665, 0.2692335, 0.2307665, 0.2692335]


def _illusory_chain(n):
    out = [int(np.random.choice(4, p=ILLUSORY_STATIONARY))]
    for _ in range(n - 1):
        row = np.array(ILLUSORY_P[out[-1]]); row = row / row.sum()
        out.append(int(np.random.choice(4, p=row)))
    return out


class SerialReactionExp1:
    """Experiment 2 of Wu et al. (2023), "Chunking as a rational solution to the
    speed-accuracy trade-off in a serial reaction time task", Scientific Reports
    13, 7680. Design: "Serial reaction time task" (Methods, p. 2) and Fig. 1.

    12 blocks x 100 trials: 2 baseline, 6 training, 2 test, then a practice and an
    instruction (free-press) block. Every block's cues come from the same
    non-deterministic "illusory" first-order Markov transition matrix (Fig. 1c),
    so the two conditions differ only by instruction: condition 0 (fast) responds
    as fast as possible during training; condition 1 (accurate) as accurately as
    possible. The abstract letters A/B/C/D map onto physical keys D/F/J/K via a
    fresh permutation per participant. In the practice block, 25 fixed trial
    positions cue no key (recorded "O"); in the instruction block no key is cued
    on any trial (recorded "fp"). On cued trials pressing the cued key is correct;
    on free-press trials the press is recorded correct.

    ASSUMPTION: reaction time is a physical measure a text simulator cannot
    reproduce; a plausible log-normal RT is drawn per trial so the narrated
    "Reaction time X ms." feedback reads naturally and the round trip reproduces
    byte-for-byte.
    ASSUMPTION: the practice-block free-press "O" trials show ~50% correct in the
    raw data (non-recoverable); here free-press trials are recorded correct = 1,
    matching the instruction block (which is exactly correct = 1 in the data).
    ASSUMPTION: block 11's instruction code is written "fp" for every participant
    (the source uses "fp" for 111 of 116 participants and "FreePress" for 5); both
    narrate identically.
    ASSUMPTION: the fixed "O" free-press positions and the recovered transition
    matrix/stationary distribution are taken from the repo's experiments/exp1
    (built to match exp1.csv), and the abstract letters are not narrated (the cued
    physical key is shown).
    """

    def __init__(self):
        self.name = "wu_2023_chunking_exp1"
        self.num_blocks = 12
        self.trials_per_block = 100
        self.conditions = [0, 1]

    def _session_blocks(self):
        main = _illusory_chain(10 * self.trials_per_block)          # blocks 0-9
        practice = _illusory_chain(self.trials_per_block)           # block 10
        by_block = [main[b * self.trials_per_block:(b + 1) * self.trials_per_block]
                    for b in range(10)]
        by_block.append(practice)                                   # block 10
        by_block.append([None] * self.trials_per_block)             # block 11 free-press
        return by_block

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            cond = int(np.random.choice(self.conditions))
            key_perm = list(np.random.permutation(PHYSICAL_KEYS))
            intro = PARA1
            intro += FAST_PARA if cond == 0 else ACCURATE_PARA
            intro += SESSION_PARA
            prompt = intro
            by_block = self._session_blocks()
            prev_phase = None
            for b in range(self.num_blocks):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                ph = PHASE_BY_BLOCK[b]
                if ph != prev_phase:
                    prompt += f"\nThis is the {ph} phase.\n"
                    prev_phase = ph
                base = b * self.trials_per_block
                for t in range(self.trials_per_block):
                    tlc = t + 1
                    if b == 11:
                        is_free, cue_code = True, "fp"
                    elif b == 10 and tlc in PRACTICE_FREE:
                        is_free, cue_code = True, "O"
                    else:
                        is_free, cue_code = False, key_perm[by_block[b][t]]
                    prompt += f"Trial {base + tlc}: "
                    if is_free:
                        prompt += "No key is cued. You press [HUMAN_RESPONSE]"
                    else:
                        prompt += f"A {cue_code} cue is shown. You press [HUMAN_RESPONSE]"
                    response = agent(prompt, choice_options=PHYSICAL_KEYS)
                    correct = 1 if (is_free or response == cue_code) else 0
                    rt = int(round(np.random.lognormal(6.15, 0.45)))
                    prompt += f"{response}[/HUMAN_RESPONSE]."
                    prompt += " Correct." if correct == 1 else " Wrong."
                    prompt += f" Reaction time {rt} ms.\n"
                    rows.append({
                        "participant_id": participant + 1, "trial": base + t,
                        "block": b, "phase": ph, "response": response, "rt": rt,
                        "correct": correct, "condition": cond,
                        "keyassignment": '["' + '", "'.join(key_perm) + '"]',
                        "trialcollect": tlc, "trialinstruction": TRIALINST[b],
                        "instructioncollect": cue_code,
                    })
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "block", "phase", "response", "rt", "correct",
            "condition", "keyassignment", "trialcollect", "trialinstruction",
            "instructioncollect",
        ])
        return df, prompts


def _random_agent(prompt, choice_options):
    return str(np.random.choice(choice_options))


def main():
    parser = argparse.ArgumentParser(description="Smoke-test this simulator with a uniform-random agent.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3)
    parser.add_argument("--max-chars", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()
    if args.seed is not None:
        np.random.seed(args.seed)
    task = SerialReactionExp1()
    df, prompts = task.simulate(_random_agent, args.num_simulations, max_chars=args.max_chars)
    print(f"name: {task.name}")
    print(f"df shape: {df.shape}")
    print("dtypes:")
    print(df.dtypes.to_string())
    print("head:")
    print(df.head(8).to_string())
    print(f"prompt lengths: {[len(p) for p in prompts]}")
    for i, p in enumerate(prompts):
        print(f"participant {i} first line: {p.splitlines()[0][:120]}")
    print("=" * 78)
    print("first prompt, head:")
    print(prompts[0][:600])
    print("...")
    print("first prompt, tail:")
    print(prompts[0][-300:])


if __name__ == "__main__":
    main()