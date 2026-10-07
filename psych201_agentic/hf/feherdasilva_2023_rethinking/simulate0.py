# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/feherdasilva_2023_rethinking``
(Feher da Silva, Lombardi, Edelson, & Hare, 2023, Nature Human Behaviour 7,
956-969), format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import random

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (INSTRUCTIONS/NOUNS), with [num_trials] resolved.
NOUNS = {
    "story": {"obj1_pl": "carpets", "place": "mountain", "obj2_pl": "lamps", "actor_pl": "genies"},
    "abstract": {"obj1_pl": "boxes", "place": "state", "obj2_pl": "lamps", "actor_pl": "genies"},
}
PAPER = "Hugging-Brain/feherdasilva_2023_rethinking"
INSTRUCTIONS = {
    "story": (
        "You will take 150 flights to the mountains and get paid for every "
        "gold coin the genies give you. You have two magic carpets. The symbol written "
        "on each carpet says which mountain it normally flies to, but if the wind is too "
        "dangerous the carpet lands on the other mountain instead. The carpets are shown "
        "on the left and right sides of the screen, and their borders glow for 2 seconds "
        "while you choose. The two carpets are marked with the symbols A and B; to choose "
        "a carpet press its symbol. The carpet flies you to a mountain, and when you wake "
        "up two lamps are glowing on that mountain, shown on the left and right. Each lamp "
        "has the name of the genie that lives inside written on it. On each mountain the "
        "two lamps are marked with the symbols A and B; to rub a lamp press its symbol. If "
        "a genie is interested in music he comes out and gives you a gold coin; otherwise "
        "he stays inside. A genie's interest may change over time, and each carpet lands "
        "more often on the mountain whose name is written on it. You must choose within 2 "
        "seconds at every step; if you are too slow the genies go to sleep and you get "
        "nothing. At every choice, press the symbol, A or B, of the option you choose."
    ),
    "abstract": (
        "You perform 150 trials and get paid for every gold coin the genies give "
        "you. Two boxes appear on the screen, shown on the left and right, and their "
        "borders glow for 2 seconds while you choose. The two boxes are marked with the "
        "symbols A and B; to choose a box press its symbol. Each box gives you a pair of "
        "lamps of one color, and the color of lamps you get determines what reward you can "
        "earn, so choose the box you think works better. After you pick a box the screen "
        "goes black and then two lamps of that color appear on the left and right. The two "
        "lamps of each color are marked with the symbols A and B; to choose a lamp press "
        "its symbol. You have 2 seconds to choose a lamp. A genie interested in music "
        "comes out of his lamp and gives you a gold coin; otherwise you get nothing. "
        "Remember from which lamps you got coins, because the lamps only change gradually. "
        "At every step, press the symbol, A or B, of the option you choose."
    ),
}
# What a missed first-stage response looks like, per condition (verbatim from build_jsonl.py).
MISS1 = {
    "story": "You fail to respond within 2 seconds, and the carpets fly away without you.\n",
    "abstract": "You fail to respond within 2 seconds and get nothing.\n",
}


def _letters(pid):
    """Verbatim from build_jsonl.py: per-participant letter names for the two symbols
    (codes 1 and 2), used at both stages; the marked token names the chosen symbol."""
    rng = random.Random(f"{PAPER}/{pid}")
    letters = ["A", "B"]
    if rng.random() < 0.5:
        letters.reverse()
    return {1: letters[0], 2: letters[1]}


class TwoStageTask:
    """Two-stage "magic carpet" decision task, Feher da Silva et al. (2023),
    Nat. Hum. Behav. 7, 956-969, exp0.

    Design (Methods, "Two-stage task"; reconstituted from exp0.csv because the
    open-access preview of the article does not expose the Methods section): 150
    blocks per participant. Each block shows two first-stage symbols (carpets in
    the ``story`` condition, boxes in ``abstract``) on the left/right, named by the
    letters A/B (letter-to-symbol map drawn per participant from a seed fixed by
    the participant id, exactly as in ``build_jsonl.py``); the agent presses the
    letter of the symbol it chooses. Choosing a symbol (value 1 or 2) transitions to second-stage
    state ``symbol`` on a common trial (p = 0.7) and to the other state on a rare
    trial; in the data ``final_state == choice symbol`` exactly when
    ``common == 1``. The states hold two second-stage symbols each; the agent
    presses A/B among them and receives a coin with probability
    ``reward_prob_{state}_{symbol}``. Participants in the ``story`` condition
    receive the cover-story instructions, the rest the abstract ones (94
    participants; 46 story, 48 abstract).

    ASSUMPTION: the four reward probabilities per participant drift as plain
    reflected random walks on [0.25, 0.75] with gaussian(0, 0.025) steps and a
    uniform(0.25, 0.75) start (matches exp0.csv's increments and start
    distribution, and mirrors the documented jsExperiment port). The four walks
    are drawn independently.

    ASSUMPTION: first-stage and second-stage symbol placement (which of the two
    symbols shows on the left) is randomized per block with probability 1/2; the
    data show roughly half of each arrangement per participant.

    ASSUMPTION: a miss (slow) trial occurs with probability ~0.01 at each stage;
    ``slow`` is a trial-level flag (1 if either stage response was missed) and
    ``valid`` is per row, exactly as in exp0.csv. A missed stage-1 response
    leaves ``final_state`` empty for the block.

    ASSUMPTION: the post-task ratings (``understanding``, ``effort``,
    ``complexity``, 0-4) and ``runs`` (~3) are drawn per participant from their
    observed distributions in exp0.csv.

    The DataFrame matches exp0.csv minus the reaction-time columns (``rt1``,
    ``rt2``, ``rt``), which a text simulator cannot produce.
    """

    def __init__(self):
        self.name = "feherdasilva_2023_rethinking_exp0"
        self.num_trials = 150
        self.common_prob = 0.7
        self.run_min, self.run_max = 0.25, 0.75
        self.run_sd = 0.025
        self.miss_prob = 0.01

    def _walk(self, n):
        v = np.random.uniform(self.run_min, self.run_max)
        out = []
        lo, hi, sd, rng = (self.run_min, self.run_max, self.run_sd, np.random)
        for _ in range(n):
            v = v + rng.normal(0.0, sd)
            if v < lo:
                v = lo + (lo - v)
            elif v > hi:
                v = hi - (v - hi)
            out.append(v)
        return np.array(out)

    def simulate(self, agent, num_simulations, max_chars=None):
        columns = [
            "participant_id", "condition", "runs", "understanding", "effort", "complexity",
            "block", "phase", "trial_number", "common",
            "reward_prob_1_1", "reward_prob_1_2", "reward_prob_2_1", "reward_prob_2_2",
            "isymbol_lft", "isymbol_rgt", "final_state",
            "fsymbol_lft", "fsymbol_rgt", "choice1", "choice2", "slow",
            "stage", "response", "state", "reward", "valid", "trial",
        ]
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            # per-participant constants, as in exp0.csv / build_jsonl metadata
            condition = "story" if np.random.rand() < 0.5 else "abstract"
            nouns = NOUNS[condition]
            L = _letters(participant)
            inv = {v: k for k, v in L.items()}
            runs = float(np.random.choice([1, 2, 3, 3, 3, 4]))
            understanding = float(np.random.randint(0, 5))
            effort = float(np.random.randint(0, 5))
            complexity = float(np.random.randint(0, 5))
            # four drifting reward probabilities, one per (state, symbol) pair
            p11, p12 = self._walk(self.num_trials), self._walk(self.num_trials)
            p21, p22 = self._walk(self.num_trials), self._walk(self.num_trials)
            prompt = INSTRUCTIONS[condition] + "\n"
            for block in range(self.num_trials):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                # which symbol is shown on the left at each stage
                ilft = np.random.randint(1, 3)
                irgt = 3 - ilft
                flft = np.random.randint(1, 3)
                frgt = 3 - flft
                # --- stage 1 ---
                trial = 2 * block
                common = 1 if np.random.rand() < self.common_prob else 0
                miss1 = np.random.rand() < self.miss_prob
                slow = 1 if miss1 else 0
                if miss1:
                    prompt += MISS1[condition]
                    rows.append({
                        "participant_id": participant, "condition": condition,
                        "runs": runs, "understanding": understanding, "effort": effort,
                        "complexity": complexity, "block": block, "phase": "test",
                        "trial_number": block, "common": common,
                        "reward_prob_1_1": p11[block], "reward_prob_1_2": p12[block],
                        "reward_prob_2_1": p21[block], "reward_prob_2_2": p22[block],
                        "isymbol_lft": ilft, "isymbol_rgt": irgt, "final_state": np.nan,
                        "fsymbol_lft": np.nan, "fsymbol_rgt": np.nan,
                        "choice1": np.nan, "choice2": np.nan, "slow": 1,
                        "stage": "stage1", "response": np.nan, "state": 0.0,
                        "reward": np.nan, "valid": 0, "trial": trial,
                    })
                    rows.append({
                        "participant_id": participant, "condition": condition,
                        "runs": runs, "understanding": understanding, "effort": effort,
                        "complexity": complexity, "block": block, "phase": "test",
                        "trial_number": block, "common": common,
                        "reward_prob_1_1": p11[block], "reward_prob_1_2": p12[block],
                        "reward_prob_2_1": p21[block], "reward_prob_2_2": p22[block],
                        "isymbol_lft": ilft, "isymbol_rgt": irgt, "final_state": np.nan,
                        "fsymbol_lft": np.nan, "fsymbol_rgt": np.nan,
                        "choice1": np.nan, "choice2": np.nan, "slow": 1,
                        "stage": "stage2", "response": np.nan, "state": np.nan,
                        "reward": 0.0, "valid": 0, "trial": trial + 1,
                    })
                    continue
                prompt += (
                    f"Two {nouns['obj1_pl']} appear: the left one has symbol {L[ilft]}, "
                    f"the right one has symbol {L[irgt]}. You press [HUMAN_RESPONSE]"
                )
                key1 = agent(prompt, choice_options=["A", "B"])
                chosen_sym = inv[key1]
                prompt += f"{key1}[/HUMAN_RESPONSE].\n"
                final_state = chosen_sym if common == 1 else 3 - chosen_sym
                # --- stage 2 ---
                place = f"{nouns['place']} {int(final_state)}"
                miss2 = np.random.rand() < self.miss_prob
                slow = 1 if miss2 else 0
                if miss2:
                    prompt += (
                        f"You land on {place}. Two {nouns['obj2_pl']} appear: the left "
                        f"one has symbol {L[flft]}, the right one has symbol {L[frgt]}. "
                        f"You fail to respond within 2 seconds, the {nouns['actor_pl']} "
                        "go to sleep, and you get nothing.\n"
                    )
                    rows.append({
                        "participant_id": participant, "condition": condition,
                        "runs": runs, "understanding": understanding, "effort": effort,
                        "complexity": complexity, "block": block, "phase": "test",
                        "trial_number": block, "common": common,
                        "reward_prob_1_1": p11[block], "reward_prob_1_2": p12[block],
                        "reward_prob_2_1": p21[block], "reward_prob_2_2": p22[block],
                        "isymbol_lft": ilft, "isymbol_rgt": irgt,
                        "final_state": float(final_state), "fsymbol_lft": flft,
                        "fsymbol_rgt": frgt, "choice1": float(chosen_sym),
                        "choice2": np.nan, "slow": 1, "stage": "stage1",
                        "response": float(chosen_sym - 1), "state": 0.0,
                        "reward": np.nan, "valid": 1, "trial": trial,
                    })
                    rows.append({
                        "participant_id": participant, "condition": condition,
                        "runs": runs, "understanding": understanding, "effort": effort,
                        "complexity": complexity, "block": block, "phase": "test",
                        "trial_number": block, "common": common,
                        "reward_prob_1_1": p11[block], "reward_prob_1_2": p12[block],
                        "reward_prob_2_1": p21[block], "reward_prob_2_2": p22[block],
                        "isymbol_lft": ilft, "isymbol_rgt": irgt,
                        "final_state": float(final_state), "fsymbol_lft": flft,
                        "fsymbol_rgt": frgt, "choice1": float(chosen_sym),
                        "choice2": np.nan, "slow": 1, "stage": "stage2",
                        "response": np.nan, "state": float(final_state - 1),
                        "reward": 0.0, "valid": 0, "trial": trial + 1,
                    })
                    continue
                prompt += (
                    f"You land on {place}. Two {nouns['obj2_pl']} appear: the left "
                    f"one has symbol {L[flft]}, the right one has symbol {L[frgt]}. "
                )
                prompt += "You press [HUMAN_RESPONSE]"
                key2 = agent(prompt, choice_options=["A", "B"])
                chosen_sym2 = inv[key2]
                prob_reward = (
                    p11[block] if final_state == 1 and chosen_sym2 == 1 else
                    p12[block] if final_state == 1 else
                    p21[block] if chosen_sym2 == 1 else p22[block]
                )
                reward = 1 if np.random.rand() < prob_reward else 0
                prompt += f"{key2}[/HUMAN_RESPONSE]."
                prompt += " You receive a gold coin.\n" if reward else " You receive nothing.\n"
                rows.append({
                    "participant_id": participant, "condition": condition,
                    "runs": runs, "understanding": understanding, "effort": effort,
                    "complexity": complexity, "block": block, "phase": "test",
                    "trial_number": block, "common": common,
                    "reward_prob_1_1": p11[block], "reward_prob_1_2": p12[block],
                    "reward_prob_2_1": p21[block], "reward_prob_2_2": p22[block],
                    "isymbol_lft": ilft, "isymbol_rgt": irgt,
                    "final_state": float(final_state), "fsymbol_lft": flft,
                    "fsymbol_rgt": frgt, "choice1": float(chosen_sym),
                    "choice2": float(chosen_sym2), "slow": 0, "stage": "stage1",
                    "response": float(chosen_sym - 1), "state": 0.0,
                    "reward": np.nan, "valid": 1, "trial": trial,
                })
                rows.append({
                    "participant_id": participant, "condition": condition,
                    "runs": runs, "understanding": understanding, "effort": effort,
                    "complexity": complexity, "block": block, "phase": "test",
                    "trial_number": block, "common": common,
                    "reward_prob_1_1": p11[block], "reward_prob_1_2": p12[block],
                    "reward_prob_2_1": p21[block], "reward_prob_2_2": p22[block],
                    "isymbol_lft": ilft, "isymbol_rgt": irgt,
                    "final_state": float(final_state), "fsymbol_lft": flft,
                    "fsymbol_rgt": frgt, "choice1": float(chosen_sym),
                    "choice2": float(chosen_sym2), "slow": 0, "stage": "stage2",
                    "response": float(chosen_sym2 - 1), "state": float(final_state - 1),
                    "reward": float(reward), "valid": 1, "trial": trial + 1,
                })
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=columns)
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

    task = TwoStageTask()
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