# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 (Experiment 1: chunk generation) of
``Hugging-Brain/wu_2023_chunking``, format-identical to ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim narration templates from build_jsonl.py (transcribe_exp0).
PARA1 = (
    "You take part in a serial reaction time experiment. On each trial, one of the "
    "four keys D, F, J, or K is displayed as the instruction cue, and you must press "
    "the corresponding key on the keyboard. Press D for the key labeled D, F for F, "
    "J for J, and K for K. Respond as fast and accurately as possible; your bonus "
    "depends on both your reaction time and your accuracy.\n")
PARA2 = ("The session has 2 baseline blocks, then 6 training blocks, then 2 test "
         "blocks; each block has 100 trials. After each trial you see your reaction "
         "time and whether you were correct, then the next trial begins after a short "
         "interval.\n")
BEGIN = "\nYou begin the baseline blocks.\n"

PHYSICAL_KEYS = ["D", "F", "J", "K"]
PHASE_BY_BLOCK = {0: "baseline", 1: "baseline", 2: "training", 3: "training",
                  4: "training", 5: "training", 6: "training", 7: "training",
                  8: "test", 9: "test"}

# "Illusory" first-order Markov matrix over abstract indices A,B,C,D (paper Fig. 1c).
# A->B = C->D = 0.9 (high); B->C = D->A = 0.7 (medium); rest spread uniformly.
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


def _independent_chain(n):
    return [int(x) for x in np.random.randint(0, 4, size=n)]


def _chunk_chain(n, chunks, probs):
    seq = []
    while len(seq) < n:
        c = int(np.random.choice(len(chunks), p=probs))
        seq.extend(chunks[c])
    return seq[:n]


class SerialReactionExp0:
    """Experiment 1 of Wu et al. (2023), "Chunking as a rational solution to the
    speed-accuracy trade-off in a serial reaction time task", Scientific Reports
    13, 7680. Design: "Serial reaction time task" (Methods, p. 2) and Fig. 1.

    Each participant does 10 blocks x 100 trials (2 baseline, 6 training, 2 test).
    Baseline and test cues come from the non-deterministic first-order Markov
    "illusory" transition matrix (Fig. 1c). Training cues are condition specific:
    condition 0 (independent) = iid uniform over A/B/C/D; condition 1 (size-3) =
    chunks ABC, D with p=1/2; condition 2 (size-2) = chunks AB, C, D with p=1/3
    each. The abstract letters A/B/C/D are mapped onto the physical keys D/F/J/K
    by a fresh random permutation per participant. On each trial the participant
    presses one of the four physical keys; pressing the cued key is correct.

    ASSUMPTION: reaction time is a psychophysical measure a text simulator cannot
    reproduce, so a plausible log-normal RT is drawn per trial (data median ~470
    ms) purely so the narrated "Reaction time X ms." feedback reads naturally and
    the round-trip narration reproduces byte-for-byte.
    ASSUMPTION: the chunk condition is assigned uniformly at random and is NOT
    narrated as informing the participant which chunk structure they must learn
    (the paper assigns between-subject groups without stating they are told).
    ASSUMPTION: each phase-run starts from the matrix's stationary distribution
    and the residual probability in each row is spread uniformly over the three
    non-target keys, matching the empirically observed baseline/test transition
    counts in exp0.csv.
    """

    def __init__(self):
        self.name = "wu_2023_chunking_exp0"
        self.num_blocks = 10
        self.trials_per_block = 100
        self.conditions = [0, 1, 2]

    def _session_blocks(self, cond):
        baseline = _illusory_chain(2 * self.trials_per_block)
        if cond == 0:
            training = _independent_chain(6 * self.trials_per_block)
        elif cond == 1:
            training = _chunk_chain(6 * self.trials_per_block, [[0, 1, 2], [3]], [0.5, 0.5])
        else:
            training = _chunk_chain(6 * self.trials_per_block, [[0, 1], [2], [3]],
                                    [1 / 3, 1 / 3, 1 / 3])
        test = _illusory_chain(2 * self.trials_per_block)
        allseq = baseline + training + test
        return [allseq[b * self.trials_per_block:(b + 1) * self.trials_per_block]
                for b in range(self.num_blocks)]

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            cond = int(np.random.choice(self.conditions))
            key_perm = list(np.random.permutation(PHYSICAL_KEYS))
            prompt = PARA1 + PARA2 + BEGIN
            by_block = self._session_blocks(cond)
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
                    cue = key_perm[by_block[b][t]]
                    prompt += f"Trial {base + t + 1}: A {cue} cue is shown. You press [HUMAN_RESPONSE]"
                    response = agent(prompt, choice_options=PHYSICAL_KEYS)
                    correct = 1 if response == cue else 0
                    rt = int(round(np.random.lognormal(6.15, 0.45)))
                    prompt += f"{response}[/HUMAN_RESPONSE]."
                    prompt += " Correct." if correct == 1 else " Wrong."
                    prompt += f" Reaction time {rt} ms.\n"
                    rows.append({
                        "participant_id": f"P{participant:03d}", "trial": base + t,
                        "block": b, "phase": ph, "response": response, "rt": rt,
                        "correct": correct, "condition": cond,
                        "keyassignment": '["' + '", "'.join(key_perm) + '"]',
                        "trialcollect": t + 1, "trialinstruction": "n",
                        "instructioncollect": cue,
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
    task = SerialReactionExp0()
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