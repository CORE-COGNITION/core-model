# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/xu_2021_novelty``, format-identical
to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import random

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp0), with the letter slots kept.
INSTRUCTIONS = (
    "You are navigating a maze of 11 rooms, each shown as an image on screen. "
    "One of the rooms is the goal image; your task is to find the shortest path to it. "
    "At each room you see four grey buttons below the image. "
    "Button 1 is pressed with {l0}, button 2 with {l1}, "
    "button 3 with {l2}, button 4 with {l3}. "
    "Pressing a button moves you to the next room. "
    "You receive no feedback along the way; when you reach the goal image you earn a reward "
    "and the episode ends. You will run several episodes, each starting in a new room."
)


class NoveltySwitchState:
    """Sequential grid-world navigation task of Xu, Modirshanechi et al. (2021),
    "Novelty is not surprise", PLoS Comput Biol 17(6): e1009070.

    Design ("Results > Experimental paradigm and human behavior", p. 3, and
    Fig 1): 10 non-goal states plus the goal image (state 10 in the shipped
    data; participant-facing states 0..9 are the paper's states 1..10). Four
    free actions per trial. Each participant runs 5 episodes per block and 2
    blocks; an episode ends when the goal (state 10) is reached, which pays
    reward 1. The block division and the swap were unknown to the participants
    (paper p. 4), so the narration announces neither; episodes count 1..10. Block 1
    (env 3, paper "block 1") is the novelty/novel-state block; block 2 (env 4,
    paper "block 2") uses the environment in which two states' appearances are
    swapped. Transitions are deterministic; no partial reward along the way.

    The paper says each episode's initial state was "chosen randomly, but kept
    fixed across participants" and lists them as i(1)=6, i(2)=9, i(3)=4, i(4)=5,
    i(5)=8 (Methods, p. 21; 1-based); the shipped data show the same fixed
    starts {1: 5, 2: 8, 3: 3, 4: 4, 5: 7} (0-based, same in both blocks), and
    this simulator uses those.

    ASSUMPTION: the exact (env, state, action) -> next_state mapping is not
    printed in the paper's main text (figures show only the schematic graph);
    the deterministic transition tables below are extracted from exp0.csv,
    which fully witnesses every transition under both environments. The env-4
    tables already incorporate the paper's state-3/state-7 swap (states 2 and 6
    in the 0-based numbering).

    Per-participant button->letter mapping mirrors build_jsonl.py exactly:
    rng = random.Random(int(participant_id)); letters A-D shuffled; button
    r maps to letters[r]. The DataFrame matches exp0.csv (columns
    participant_id, trial, block, response, env, epi, state, next_state,
    reward); there is no rt to drop.
    """

    # (env, state) -> {action: next_state}; env is the raw source code
    # (block + 2); states use the 0-based paper numbering of exp0.csv (goal = 10)
    # and actions the 0-based numbering of exp0.csv.
    TRANSITIONS = {
        3: {
            0: {0: 9, 1: 0, 2: 1, 3: 8},
            1: {0: 8, 1: 2, 2: 7, 3: 1},
            2: {0: 7, 1: 8, 2: 2, 3: 3},
            3: {0: 4, 1: 9, 2: 3, 3: 8},
            4: {0: 4, 1: 9, 2: 5, 3: 7},
            5: {0: 9, 1: 6, 2: 8, 3: 5},
            6: {0: 10, 1: 8, 2: 7, 3: 6},
            7: {0: 8, 1: 7, 2: 0, 3: 9},
            8: {0: 7, 1: 0, 2: 9, 3: 8},
            9: {0: 7, 1: 8, 2: 0, 3: 9},
        },
        4: {
            0: {0: 9, 1: 0, 2: 1, 3: 8},
            1: {0: 8, 1: 6, 2: 7, 3: 1},
            2: {0: 10, 1: 8, 2: 7, 3: 2},
            3: {0: 4, 1: 9, 2: 3, 3: 8},
            4: {0: 4, 1: 9, 2: 5, 3: 7},
            5: {0: 9, 1: 2, 2: 8, 3: 5},
            6: {0: 7, 1: 8, 2: 6, 3: 3},
            7: {0: 8, 1: 7, 2: 0, 3: 9},
            8: {0: 7, 1: 0, 2: 9, 3: 8},
            9: {0: 7, 1: 8, 2: 0, 3: 9},
        },
    }
    # Fixed initial state per episode (same in both blocks), exp0.csv numbering.
    EPISODE_STARTS = {1: 5, 2: 8, 3: 3, 4: 4, 5: 7}
    GOAL = 10

    def __init__(self):
        self.name = "xu_2021_novelty_exp0"
        self.num_blocks = 2
        self.episodes_per_block = 5
        self.num_actions = 4

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            rng = random.Random(int(participant))
            letters = list("ABCD")
            rng.shuffle(letters)
            btn = {r: letters[r] for r in range(self.num_actions)}
            letter_to_action = {letters[r]: r for r in range(self.num_actions)}
            prompt = INSTRUCTIONS.format(l0=btn[0], l1=btn[1], l2=btn[2], l3=btn[3])
            trial = 0
            n_epi = 0
            for block in range(self.num_blocks):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                env = block + 3
                for epi in range(1, self.episodes_per_block + 1):
                    n_epi += 1
                    prompt += f"\nEpisode {n_epi} starts in a new room."
                    state = self.EPISODE_STARTS[epi]
                    while True:
                        prompt += f"\nYou are in room {state}. You press [HUMAN_RESPONSE]"
                        letter = agent(prompt, choice_options=list(letters))
                        response = letter_to_action[letter]
                        next_state = self.TRANSITIONS[env][state][response]
                        reward = 1 if next_state == self.GOAL else 0
                        prompt += f"{letter}[/HUMAN_RESPONSE]."
                        if next_state == self.GOAL:
                            prompt += " You reach the goal image and earn a reward."
                        else:
                            prompt += f" You move to room {next_state}. You get no reward."
                        rows.append({
                            "participant_id": participant, "trial": trial, "block": block,
                            "response": response, "env": env, "epi": epi,
                            "state": state, "next_state": next_state, "reward": reward,
                        })
                        trial += 1
                        if next_state == self.GOAL:
                            break
                        state = next_state
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "block", "response", "env", "epi",
            "state", "next_state", "reward",
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

    task = NoveltySwitchState()
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