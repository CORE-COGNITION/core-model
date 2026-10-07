# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/flesch_2018_comparing``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import hashlib

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (_main_instructions).
INSTRUCTIONS = (
    "You manage two gardens, a north and a south garden. In each garden "
    "some trees grow well and others do not. Each trial you visit one "
    "garden and see one tree; trees vary in branchiness (how many "
    "branches) and leafiness (how many leaves). Decide whether to plant "
    "the tree in that garden. Press {A} to accept (plant) the tree or "
    "{B} to reject it. You learn which trees grow well in each garden by "
    "trial and error: good choices gain points and bad choices lose points."
)
SECOND_LINE = ("You first complete 400 training trials with points feedback, "
               "then 200 test trials without feedback.")

CONDITIONS = ["b200", "b20", "b2", "interleaved"]
# Observed group sizes (exp0 = Experiment 1a): 48/41/40/47 of 176.
COND_PROBS = np.array([48, 41, 40, 47]) / 176.0

TRAIN_EXEMPLARS = ["a", "b", "c", "d"]
TEST_EXEMPLARS = ["e", "f", "g", "h"]


def _letter_map(pid):
    """Same per-participant accept/reject token policy as build_jsonl.py."""
    h = hashlib.md5(str(pid).encode("utf-8")).hexdigest()
    # Source coding is fixed: resp_category 1 = accept (plant), 0 = reject
    # (expt_response.js: resp_reward = expt_rewardIDX * resp_category); only
    # the letter assigned to each option is randomized per participant.
    accept_val = 1
    if int(h[1], 16) % 2 == 0:
        letters = {"accept": "A", "reject": "B"}
    else:
        letters = {"accept": "B", "reject": "A"}
    return accept_val, letters


def _garden(state):
    return "north" if int(state) == 0 else "south"


def _tree(b, l):
    return f"branchiness {b}, leafiness {l}"


class ContinualGardening:
    """Experiment 1a of Flesch et al. (2018), "Comparing continual task
    learning in minds and machines", PNAS 115(44):E10313-E10322. exp0 = the
    cardinal-reward version (north classifies by leafiness, south by
    branchiness).

    Design (Methods — Task and Procedure; Fig. 1D): 600 trials — 400 training
    with point feedback, 200 interleaved test without feedback — in 3 blocks
    of 200. Each trial shows one of the 25 (branchiness x leafiness) cells in
    one of two garden contexts; the participant presses an accept/reject key.
    Training context structure depends on the group: B200 (two 200-trial runs,
    one per garden), B20 (20-trial runs), B2 (2-trial runs), or Interleaved
    (random). The test block is always randomly interleaved (100 instances of
    each garden). Presentation counts are equated per condition (leafiness
    level [5] x branchiness level [5] x context [2]).

    Generative process recovered from the paper and the data (all verified
    against the 176 participants of exp0.csv):
      - Training uses exemplars a-d, each (branch, leaf, exemplar) cell exactly
        2x per garden context; test uses exemplars e-h, each (context, branch,
        leaf, exemplar) combination exactly once, so every (context, branch,
        leaf) cell appears 12 times across the session. Order per garden is a
        random shuffle per participant.
      - Reward rule (cardinal): in the north garden the leaf level sets the
        category/reward (leaf 1 = +50 ... leaf 5 = -50), in the south garden
        the branch level does (branch 1 = -50 ... branch 5 = +50); the sign of
        each garden's rule is counterbalanced per participant. Accepting a tree
        pays reward_index (positive or negative); rejecting pays 0. ``correct``
        is 1 when the response equals the optimal response (accept iff category
        >= 0; the boundary, category 0, scores correct only for accept).
      - ``return`` / ``optimal_return`` are block-wise inclusive cumulative
        sums of the (optimal) rewards, with the first trial of each 200-trial
        block recorded as 0 (source artifact, verified for all 528
        participant-blocks of exp0.csv).

    ASSUMPTION: accept/reject are rendered as the single letters A/B with
    build_jsonl.py's deterministic md5-of-participant_id mapping, so simulated
    transcripts are byte-identical to a build_jsonl round trip. Missed trials
    (NaN responses in the data) are not modeled: every trial gets a response.
    Reaction times, timestamps, demographics (age/gender_subacc/subcodes) and
    the free-text post-experiment reports are not producible by a text
    simulator and are dropped from the DataFrame.

    The DataFrame mirrors exp0.csv minus ``resp_reactiontime``,
    ``resp_timestamp``, ``age``, ``gender_code``, ``subacc``, ``subcode_0..6``
    and ``report_north``/``report_south``.
    """

    def __init__(self):
        self.name = "flesch_2018_comparing_exp0"
        self.diagonal = False
        self.num_training = 400
        self.num_test = 200
        self.num_blocks = 3
        self.block_size = 200

    def _reward_rule(self, state, b, l, dir_n, dir_s):
        if state == 0:  # north garden: leafiness axis
            d = 3 - l
            dsign = dir_n
        else:  # south garden: branchiness axis
            d = b - 3
            dsign = dir_s
        cd = int(np.clip(d, -2, 2))
        reward_index = dsign * 25 * cd
        category = dsign * (1 if d > 0 else (-1 if d < 0 else 0))
        return reward_index, category

    def _outcome(self, is_accept, reward_index, category):
        reward = float(reward_index) if is_accept else 0.0
        optimal_accept = 1 if category >= 0 else 0
        correct = 1 if (1 if is_accept else 0) == optimal_accept else 0
        optimal_reward = reward_index if category > 0 else 0
        return reward, correct, optimal_reward

    def _make_deck(self, exemplars, copies):
        deck = {0: [], 1: []}
        for s in (0, 1):
            items = [(b, l, e)
                     for b in range(1, 6) for l in range(1, 6)
                     for e in exemplars for _ in range(copies)]
            self._rng.shuffle(items)
            deck[s] = items
        return deck

    def _state_sequence(self, condition, start_state, n):
        if condition == "b200":
            half = n // 2
            return [start_state] * half + [1 - start_state] * half
        if condition == "b20":
            return (np.tile(np.repeat([start_state, 1 - start_state], 20),
                            n // 40)).tolist()
        if condition == "b2":
            return (np.tile([start_state, 1 - start_state], n // 2)).tolist()
        arr = np.array([0] * (n // 2) + [1] * (n // 2))
        self._rng.shuffle(arr)
        return arr.tolist()

    def simulate(self, agent, num_simulations, max_chars=None):
        rng = np.random.default_rng()
        self._rng = rng
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            pid = participant
            accept_val, letters = _letter_map(pid)
            condition = str(CONDITIONS[int(rng.choice(
                np.arange(len(CONDITIONS)), p=COND_PROBS))])
            dir_n = 1 if rng.random() < 0.5 else -1
            dir_s = 1 if rng.random() < 0.5 else -1
            start_state = int(rng.integers(0, 2))
            states_tr = self._state_sequence(condition, start_state,
                                             self.num_training)
            states_te = self._state_sequence("interleaved", start_state,
                                             self.num_test)
            deck_tr = self._make_deck(TRAIN_EXEMPLARS, 2)
            deck_te = self._make_deck(TEST_EXEMPLARS, 1)

            prompt = (INSTRUCTIONS.format(A=letters["accept"],
                                          B=letters["reject"])
                      + "\n" + SECOND_LINE)

            ret_acc = {0: 0.0, 1: 0.0, 2: 0.0}
            opt_acc = {0: 0.0, 1: 0.0, 2: 0.0}
            ret_first = {0: True, 1: True, 2: True}

            for blk in range(self.num_blocks):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                if blk < 2:
                    states = states_tr[blk * self.block_size:(blk + 1) * self.block_size]
                    deck, phase, session = deck_tr, "training", 1
                else:
                    states = states_te
                    deck, phase, session = deck_te, "test", 2
                for j, s in enumerate(states):
                    s = int(s)
                    b, l, e = deck[s].pop()
                    reward_index, category = self._reward_rule(s, b, l, dir_n, dir_s)
                    trial = blk * self.block_size + j
                    prompt += (f"\nIn the {_garden(s)} garden you see a "
                               f"tree with {_tree(b, l)}. You press "
                               f"[HUMAN_RESPONSE]")
                    letter = agent(prompt, choice_options=[
                        letters["accept"], letters["reject"]])
                    is_accept = letter == letters["accept"]
                    response = accept_val if is_accept else 1 - accept_val
                    reward, correct, optimal_reward = self._outcome(
                        is_accept, reward_index, category)
                    prompt += f"{letter}[/HUMAN_RESPONSE]."
                    if phase == "training":
                        if reward >= 0:
                            prompt += f" You gain {int(reward)} points."
                        else:
                            prompt += f" You lose {int(-reward)} points."
                    ret_acc[blk] += reward
                    opt_acc[blk] += optimal_reward
                    ret_val = 0.0 if ret_first[blk] else ret_acc[blk]
                    opt_val = 0.0 if ret_first[blk] else opt_acc[blk]
                    ret_first[blk] = False
                    rows.append({
                        "participant_id": pid, "trial": trial, "phase": phase,
                        "condition": condition, "block": blk, "state": s,
                        "session_index": session, "context_index": s + 1,
                        "branch_index": b, "leaf_index": l,
                        "reward_index": reward_index, "category_index": category,
                        "exemplar": e, "stimulus": f"B{b}L{l}_{e}.png",
                        "response": float(response), "correct": correct,
                        "reward": reward, "return": int(ret_val),
                        "optimal_reward": optimal_reward,
                        "optimal_return": int(opt_val),
                    })
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "phase", "condition", "block", "state",
            "session_index", "context_index", "branch_index", "leaf_index",
            "reward_index", "category_index", "exemplar", "stimulus",
            "response", "correct", "reward", "return", "optimal_reward",
            "optimal_return",
        ])
        return df, prompts


def _random_agent(prompt, choice_options=None):
    if choice_options is not None:
        return str(np.random.default_rng().choice(choice_options))
    x = round(float(np.random.uniform(160, 1440)), 2)
    y = round(float(np.random.uniform(60, 960)), 2)
    return (x, y)


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

    task = ContinualGardening()
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