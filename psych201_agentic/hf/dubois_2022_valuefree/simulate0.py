# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/dubois_2022_valuefree``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import random

import numpy as np
import pandas as pd
from tqdm import tqdm

POS_NAMES = {0: "left", 1: "middle", 2: "right"}
COLUMNS = [
    "participant_id", "block", "trial", "phase", "response", "reward",
    "forced_choice", "Block", "Blocktrial", "Horizon", "Item", "Sample", "Size",
    "PressedKey", "UnusedTree", "TreeColGroup", "TreeA", "TreeB", "TreeC", "TreeD",
    "TreeLeft", "TreeMiddle", "TreeRight", "InfoRequestNo",
]

# Verbatim from build_jsonl.py (transcribe_exp0), with the position tokens kept.
INSTRUCTIONS = (
    "You are on a farm with apple trees. On each round, three trees are presented: "
    "one on the left, one in the middle, and one on the right. Before you choose, "
    "you are shown apples that were already picked from some of the trees (initial "
    "samples), telling you roughly how good each tree is. Your goal is to pick "
    "apples so that the total size of the apples you collect is as large as "
    "possible.\n"
    "On each round you either make just ONE draw (pick one tree) or SIX draws (pick "
    "a tree up to six times, seeing the apple you get after each pick).\n"
    "To pick a tree, press the letter for its position: press A for the "
    "{ANAME} tree, B for the {BNAME} tree, and C for the {CNAME} tree.\n"
)

TYPE_OF_TREE = {1: "cs", 2: "std", 3: "nv", 4: "lv"}
TREE_OF_TYPE = {"cs": 1, "std": 2, "nv": 3, "lv": 4}


def _fmt(v):
    return f"{float(v)}"


def _make_row(pid, block, trial, forced, pos, tree, reward, sample, horizon, item,
              color_group, unused, l, m, r):
    tree_inds = {1: None, 2: None, 3: None, 4: None}
    tree_inds[tree] = 1
    return {
        "participant_id": pid,
        "block": block,
        "trial": trial,
        "phase": "test",
        "response": None if forced else float(pos),
        "reward": float(reward),
        "forced_choice": 1 if forced else 0,
        "Block": float(block // 100 + 1),
        "Blocktrial": float(block + 1),
        "Horizon": float(horizon),
        "Item": float(item),
        "Sample": float(sample),
        "Size": float(reward),
        "PressedKey": None if forced else float(pos + 1),
        "UnusedTree": float(unused),
        "TreeColGroup": float(color_group),
        "TreeA": tree_inds[1], "TreeB": tree_inds[2],
        "TreeC": tree_inds[3], "TreeD": tree_inds[4],
        "TreeLeft": float(l), "TreeMiddle": float(m), "TreeRight": float(r),
        "InfoRequestNo": 1.0,
    }


class MaggiesFarm:
    """3-armed "Maggie's Farm" apple-tree bandit, Experiment 1 of Dubois & Hauser
    (2022), "Value-free random exploration is linked to impulsivity", Nat. Commun.
    13:4542. Design (Methods p. 10-11; cf. Supplementary Information): each
    participant plays 400 games (100 reward Items, each used 4x = 2 short-horizon
    (1 draw) + 2 long-horizon (6 draws)); on each game 3 of the 4 bandit "types"
    are presented as trees (one omitted); each type has a fixed mean and a fixed
    number of initial samples; rewards (apple sizes) ~ round(N(mu, 0.8)) truncated
    to [2,10]. The type->tree mapping is fixed: TreeA=certain-standard (3
    samples), TreeB=standard (1 sample), TreeC=novel (0 samples), TreeD=low-value
    (1 sample); tree positions and colour group are shuffled each game.

    Means: certain-standard overall mean is 4.5 or 6.5; standard = cs + uniform
    {-2,-1,+1,+2}; novel = (cs or std) + uniform {-2,-1,+1,+2}; low-value =
    min(cs,std,novel) - 1; each type's mu ~ N(overall_mean, 1.4).

    ASSUMPTION: exp0.csv's type->tree mapping is fixed (A=cs, B=std, C=novel,
    D=low) and the omitted type per item is balanced (25 items per omitted type);
    tree positions and colour group (TreeColGroup 1..8) are shuffled per game.
    ASSUMPTION: the low-value bandit's single initial sample is always strictly
    the smallest of the item's initial samples (exp0.csv has no violations),
    reproduced by regenerating the item until the constraint holds.
    ASSUMPTION: initial samples are fixed per item (identical across the item's 4
    games, per exp0.csv), so the reveal values/order are drawn once per item;
    tree positions and colour group (TreeColGroup 1..8) still shuffle each game.
    ASSUMPTION: `rt` and `BlockDuration` are real measured columns a text
    simulator cannot reproduce, so they are dropped (as in the reference example).

    The DataFrame matches exp0.csv minus ``rt`` and ``BlockDuration``.
    """

    def __init__(self):
        self.name = "dubois_2022_valuefree_exp0"
        self.num_items = 100          # reward schedules ("Item" 1..100)
        self.uses_per_item = 4        # 2 short + 2 long per item -> 400 games
        self.short_draws = 1          # short horizon (Horizon code 6)
        self.long_draws = 6           # long horizon (Horizon code 11)
        self.sampling_sd = 0.8        # reward ~ round(N(mu, sd)) truncated [2,10]
        self.mu_sd = 1.4              # type mean mu ~ N(overall_mean, mu_sd)
        self.reward_min, self.reward_max = 2, 10
        self.cs_bases = [4.5, 6.5]
        self.offsets = [-2, -1, 1, 2]
        self.init_counts = {"cs": 3, "std": 1, "nv": 0, "lv": 1}

    def _sample_apple(self, mu):
        v = float(np.clip(np.random.normal(mu, self.sampling_sd),
                          self.reward_min, self.reward_max))
        return float(np.round(v))

    def _make_reveals(self, presented, means):
        """Initial-sample reveal sequence for one item: fixed per item (each item
        is used 4x with the same reveals, per exp0.csv). When the low-value tree
        (4) is presented, resample until its single apple is strictly the smallest
        (exp0.csv has no violations); returns None if the means make that
        impossible (every competing sample pinned at the reward floor), so the
        caller can re-roll the whole item."""
        for _ in range(2000):
            samples = []
            for tree in presented:
                ty = TYPE_OF_TREE[tree]
                cnt = self.init_counts[ty]
                mu = means[ty]
                for _ in range(cnt):
                    samples.append((tree, self._sample_apple(mu)))
            lv = [s for s in samples if s[0] == 4]
            if not lv or lv[0][1] < min(v for (t, v) in samples if t != 4):
                random.shuffle(samples)
                return samples
        return None

    def _make_items(self):
        """100 items per participant: per-type means, a balanced omitted type, and
        the fixed initial-sample reveal sequence for the item."""
        omitted = ["cs", "std", "nv", "lv"] * (self.num_items // 4)
        np.random.shuffle(omitted)
        items = []
        for i in range(self.num_items):
            # regenerate an item until its low-value reveal, if any, is smallest
            while True:
                base_cs = float(np.random.choice(self.cs_bases))
                base_std = base_cs + int(np.random.choice(self.offsets))
                nv_base = float(np.random.choice([base_cs, base_std]))
                base_nv = nv_base + int(np.random.choice(self.offsets))
                base_lv = min(base_cs, base_std, base_nv) - 1
                means = {
                    "cs": float(np.random.normal(base_cs, self.mu_sd)),
                    "std": float(np.random.normal(base_std, self.mu_sd)),
                    "nv": float(np.random.normal(base_nv, self.mu_sd)),
                    "lv": float(np.random.normal(base_lv, self.mu_sd)),
                }
                omitted_type = omitted[i]
                presented = [t for t in (1, 2, 3, 4)
                             if t != TREE_OF_TYPE[omitted_type]]
                reveals = self._make_reveals(presented, means)
                if reveals is not None:
                    items.append({"id": i + 1, "omitted": omitted_type,
                                  "means": means, "reveals": reveals})
                    break
        return items

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            items = self._make_items()
            slots = []
            for it in items:
                for hz in (6, 6, 11, 11):
                    slots.append((it, hz))

            pid = f"user_{participant}"
            rng = random.Random(pid)
            positions = [0, 1, 2]
            rng.shuffle(positions)
            letter_pos = {letter: pos for letter, pos in zip("ABC", positions)}

            prompt = INSTRUCTIONS.format(
                ANAME=POS_NAMES[letter_pos["A"]],
                BNAME=POS_NAMES[letter_pos["B"]],
                CNAME=POS_NAMES[letter_pos["C"]],
            )

            game_order = list(slots)
            rng.shuffle(game_order)
            trial_i = 0

            for block, (item, horizon) in enumerate(game_order):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                draws = self.long_draws if horizon == 11 else self.short_draws
                unused = TREE_OF_TYPE[item["omitted"]]
                presented = [t for t in (1, 2, 3, 4) if t != unused]
                shuffled_pos = list(positions)
                rng.shuffle(shuffled_pos)
                pos_of_tree = {tree: pos for tree, pos in zip(presented, shuffled_pos)}
                tree_at_pos = {pos: tree for tree, pos in pos_of_tree.items()}
                color_group = int(np.random.randint(1, 9))

                draws_word = "SIX draws" if draws == 6 else "ONE draw"
                prompt += f"A new round starts. You have {draws_word} in this round.\n"

                sample = 0
                for tree, value in item["reveals"]:
                    sample += 1
                    pos = pos_of_tree[tree]
                    prompt += (f"You see an initial sample: an apple of size "
                               f"{_fmt(value)} is hanging on the {POS_NAMES[pos]} "
                               f"tree.\n")
                    rows.append(_make_row(pid, block, trial_i, True, None, tree,
                                          value, sample, horizon, item["id"],
                                          color_group, unused, tree_at_pos[0],
                                          tree_at_pos[1], tree_at_pos[2]))
                    trial_i += 1

                for _ in range(draws):
                    sample += 1
                    prompt += "You press [HUMAN_RESPONSE]"
                    letter = agent(prompt, choice_options=["A", "B", "C"])
                    pos = letter_pos[letter]
                    tree = tree_at_pos[pos]
                    value = self._sample_apple(item["means"][TYPE_OF_TREE[tree]])
                    prompt += (f"{letter}[/HUMAN_RESPONSE] to pick the "
                               f"{POS_NAMES[pos]} tree and get an apple of size "
                               f"{_fmt(value)}.\n")
                    rows.append(_make_row(pid, block, trial_i, False, pos, tree,
                                          value, sample, horizon, item["id"],
                                          color_group, unused, tree_at_pos[0],
                                          tree_at_pos[1], tree_at_pos[2]))
                    trial_i += 1

            prompts.append(prompt.strip())

        df = pd.DataFrame(rows, columns=COLUMNS)
        df["response"] = pd.to_numeric(df["response"], errors="coerce")
        df["PressedKey"] = pd.to_numeric(df["PressedKey"], errors="coerce")
        return df, prompts


def _random_agent(prompt, choice_options):
    return str(np.random.choice(choice_options))


def main():
    parser = argparse.ArgumentParser(
        description="Smoke-test this simulator with a uniform-random agent.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3,
                        help="number of simulated participants (default: 3)")
    parser.add_argument("--max-chars", type=int, default=None,
                        help="stop each participant at the block boundary at/past "
                             "this many chars")
    parser.add_argument("--seed", type=int, default=None,
                        help="numpy random seed, for reproducible runs")
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    task = MaggiesFarm()
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