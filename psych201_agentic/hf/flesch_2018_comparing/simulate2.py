# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp2 of ``Hugging-Brain/flesch_2018_comparing``,
format-identical to the repo's ``transcripts2.jsonl``.

``uv run simulate2.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import hashlib

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (_main_instructions / _rating_instructions).
INSTRUCTIONS = (
    "You manage two gardens, a north and a south garden. In each garden "
    "some trees grow well and others do not. Each trial you visit one "
    "garden and see one tree; trees vary in branchiness (how many "
    "branches) and leafiness (how many leaves). Decide whether to plant "
    "the tree in that garden. Press {A} to accept (plant) the tree or "
    "{B} to reject it. You learn which trees grow well in each garden by "
    "trial and error: good choices gain points and bad choices lose points."
)
RATING_INSTRUCTIONS = (
    "In the rating task you arrange trees by similarity on a 2D canvas: "
    "similar trees should end up near each other and dissimilar trees "
    "far apart. On each trial one tree appears and you drag it to a "
    "position; the placement is your response."
)
PHASE_LINES = {
    "rating_pre": "The rating task: arrange each tree by similarity on a 2D canvas.",
    "training": ("Now the gardening task: 400 training trials with points "
                 "feedback, then 200 test trials without feedback."),
    "test": "Now the test trials: no feedback is given.",
    "rating_post": "You do the rating task again.",
}

CONDITIONS = ["b200", "interleaved"]
# Observed group sizes (exp2 = Experiment 2a): 68/70 of 138.
COND_PROBS = np.array([68, 70]) / 138.0

TRAIN_EXEMPLARS = ["a", "b", "c", "d"]
TEST_EXEMPLARS = ["e", "f", "g", "h"]
RATING_EXEMPLARS = list("abcdefgh")


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


class GardeningRatingTask:
    """Experiment 2a of Flesch et al. (2018), "Comparing continual task
    learning in minds and machines", PNAS 115(44):E10313-E10322. exp2 = the
    cardinal-reward version (north classifies by leafiness, south by
    branchiness) with B200 and Interleaved training groups only, plus the
    pre/post dissimilarity-placement rating sessions.

    Design (Methods — Task and Procedure; Fig. 4): before and after the main
    gardening task (identical to experiment 1), participants drag trees into a
    circular arena on a 2D canvas to express subjective dissimilarity. Main
    task: 600 trials in 3 blocks of 200 (400 training with point feedback, 200
    interleaved test without feedback). Rating sessions: 150 trials each.

    Generative process recovered from the paper and the data (all verified
    against the 138 participants of exp2.csv):
      - Main task: training uses exemplars a-d (each (branch, leaf, exemplar)
        cell exactly 2x per garden context), test uses exemplars e-h (each
        (context, branch, leaf, exemplar) combination exactly once); every
        (context, branch, leaf) cell appears 12 times across the session. B200
        trains the two gardens in two 200-trial runs, Interleaved in random
        order (balanced 200/200); the test block is randomly interleaved
        (100 per garden).
      - Rating sessions: 150 trials = 6 repetitions of the 25 cells in the
        fixed order (B1L1..B1L5, B2L1.., ..., B5L5); ``rating_index`` is the
        repetition number 1..6. The response is the participant's final
        placement (x_final, y_final) on the canvas; response is recorded as
        ``[x_final, y_final]``.
      - Reward rule (cardinal): in the north garden the leaf level sets the
        category/reward (leaf 1 = +50 ... leaf 5 = -50), in the south garden
        the branch level does (branch 1 = -50 ... branch 5 = +50); the sign is
        counterbalanced per participant. Accepting pays reward_index
        (positive or negative), rejecting pays 0; ``correct`` = 1 when the
        response equals the optimal response (accept iff category >= 0).
      - ``return`` / ``optimal_return`` are block-wise inclusive cumulative
        sums of the (optimal) rewards, the first trial of each 200-trial block
        recorded as 0 (verified against all participant-blocks of exp2.csv).

    ASSUMPTION: accept/reject are rendered as the letters A/B with
    build_jsonl.py's deterministic md5-of-participant_id mapping, so simulated
    transcripts are byte-identical to a build_jsonl round trip. Rating
    placements are the agent's free response; the initial canvas position
    (x_orig, y_orig) is drawn uniformly on the canvas and the rating stimulus
    exemplar uniformly from a-h — neither enters the transcript. Missed main
    trials are not modeled. RTs, timestamps, source subcodes, the free-text
    reports and the rating-session metadata (boundary_index, rating_sex/age/
    task, rating_start/finish_time) are not producible by a text simulator and
    are dropped from the DataFrame.

    The DataFrame mirrors exp2.csv minus ``resp_reactiontime``,
    ``resp_timestamp``, ``subcode_0..6``, ``report_north``/``report_south``,
    ``boundary_index``, ``rating_sex``, ``rating_age``, ``rating_task``,
    ``rating_start_time`` and ``rating_finish_time``.
    """

    def __init__(self):
        self.name = "flesch_2018_comparing_exp2"
        self.diagonal = False
        self.num_rating = 150
        self.num_training = 400
        self.num_test = 200
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
        arr = np.array([0] * (n // 2) + [1] * (n // 2))
        self._rng.shuffle(arr)
        return arr.tolist()

    def _rating_block(self, agent, prompt, trial, pid, condition, phase, rows):
        for rep in range(6):  # rating_index 1..6
            for cell in range(25):
                b = cell // 5 + 1
                l = cell % 5 + 1
                e = RATING_EXEMPLARS[int(self._rng.integers(0, 8))]
                x_orig = round(float(self._rng.uniform(160, 1440)), 2)
                y_orig = round(float(self._rng.uniform(60, 960)), 2)
                prompt += (f"\nA tree with {_tree(b, l)} appears. You place "
                           f"it at [HUMAN_RESPONSE]")
                x_final, y_final = agent(prompt)
                x_final = float(x_final)
                y_final = float(y_final)
                prompt += f"{[x_final, y_final]}[/HUMAN_RESPONSE]."
                rows.append({
                    "participant_id": pid, "trial": trial, "phase": phase,
                    "condition": condition,
                    "block": 0.0 if phase == "rating_pre" else 3.0, "state": np.nan,
                    "session_index": np.nan, "context_index": np.nan,
                    "branch_index": b, "leaf_index": l,
                    "reward_index": np.nan, "category_index": np.nan,
                    "exemplar": np.nan, "stimulus": f"B{b}L{l}_{e}.png",
                    "response": str([x_final, y_final]),
                    "correct": np.nan, "reward": np.nan, "return": np.nan,
                    "optimal_reward": np.nan, "optimal_return": np.nan,
                    "rating_index": rep + 1, "x_orig": x_orig, "y_orig": y_orig,
                    "x_final": x_final, "y_final": y_final,
                })
                trial += 1
        return prompt, trial

    def _main_block(self, agent, prompt, trial, pid, letters, accept_val,
                    condition, dir_n, dir_s, states, deck, phase, blk,
                    rows, ret_acc, opt_acc, ret_first):
        session = 1 if phase == "training" else 2
        for s in states:
            s = int(s)
            b, l, e = deck[s].pop()
            reward_index, category = self._reward_rule(s, b, l, dir_n, dir_s)
            prompt += (f"\nIn the {_garden(s)} garden you see a tree with "
                       f"{_tree(b, l)}. You press [HUMAN_RESPONSE]")
            letter = agent(prompt, choice_options=[letters["accept"],
                                                   letters["reject"]])
            is_accept = letter == letters["accept"]
            response = accept_val if is_accept else 1 - accept_val
            reward = float(reward_index) if is_accept else 0.0
            optimal_accept = 1 if category >= 0 else 0
            correct = 1 if (1 if is_accept else 0) == optimal_accept else 0
            optimal_reward = reward_index if category > 0 else 0
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
                "condition": condition, "block": float(blk), "state": float(s),
                "session_index": float(session), "context_index": float(s + 1),
                "branch_index": b, "leaf_index": l,
                "reward_index": float(reward_index),
                "category_index": float(category),
                "exemplar": e, "stimulus": f"B{b}L{l}_{e}.png",
                "response": float(response), "correct": float(correct),
                "reward": float(reward), "return": float(ret_val),
                "optimal_reward": float(optimal_reward),
                "optimal_return": float(opt_val),
                "rating_index": np.nan, "x_orig": np.nan, "y_orig": np.nan,
                "x_final": np.nan, "y_final": np.nan,
            })
            trial += 1
        return prompt, trial

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

            prompt = (RATING_INSTRUCTIONS + " "
                      + INSTRUCTIONS.format(A=letters["accept"],
                                            B=letters["reject"]))
            trial = 0

            ret_acc = {0: 0.0, 1: 0.0, 2: 0.0}
            opt_acc = {0: 0.0, 1: 0.0, 2: 0.0}
            ret_first = {0: True, 1: True, 2: True}

            prompt += "\n" + PHASE_LINES["rating_pre"]
            if max_chars is None or len(prompt) < max_chars:
                prompt, trial = self._rating_block(
                    agent, prompt, trial, pid, condition, "rating_pre", rows)

            prompt += "\n" + PHASE_LINES["training"]
            for blk in (0, 1):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                states = states_tr[blk * self.block_size:(blk + 1) * self.block_size]
                prompt, trial = self._main_block(
                    agent, prompt, trial, pid, letters, accept_val,
                    condition, dir_n, dir_s, states, deck_tr, "training",
                    blk, rows, ret_acc, opt_acc, ret_first)

            prompt += "\n" + PHASE_LINES["test"]
            if max_chars is None or len(prompt) < max_chars:
                prompt, trial = self._main_block(
                    agent, prompt, trial, pid, letters, accept_val,
                    condition, dir_n, dir_s, states_te, deck_te, "test", 2,
                    rows, ret_acc, opt_acc, ret_first)

            prompt += "\n" + PHASE_LINES["rating_post"]
            if max_chars is None or len(prompt) < max_chars:
                prompt, trial = self._rating_block(
                    agent, prompt, trial, pid, condition, "rating_post", rows)

            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "phase", "condition", "block", "state",
            "session_index", "context_index", "branch_index", "leaf_index",
            "reward_index", "category_index", "exemplar", "stimulus",
            "response", "correct", "reward", "return", "optimal_reward",
            "optimal_return", "rating_index", "x_orig", "y_orig", "x_final",
            "y_final",
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

    task = GardeningRatingTask()
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