# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/nussenbaum_2023_novelty``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.

The task (Nussenbaum et al., 2023, eLife 12:e84260) has two parts:
  1. Exploration: 10 blocks of 15 free choices. Each block a new creature hides
     coins among 3 hiding spots; the participant sees two of the three spots per
     trial and picks one. Reward probabilities (per spot) are re-randomized each
     block (EASY {.2,.5,.8}, HARD {.3,.5,.7} shuffled); spots are novel (never
     offered) or familiar (offered >3 times). A held-out spot is introduced at a
     fixed trial per block.
  2. Surprise memory test: 10 probes, one per creature, recalling which of 5
     shown hiding spots was that creature's high-reward favorite.

Generated data match ``exp0.csv`` minus ``rt`` and demographics/psychometrics
(age, gender, iq, WASI_*, nativeEnglish), which a text simulator cannot produce.
"""

import argparse
import json

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim narration strings from build_jsonl.py (transcribe_exp0).
INSTRUCTIONS = (
    "An enchanted kingdom needs gold coins to build a bridge to unite two sides. "
    "Various creatures have hidden coins in hiding spots around different territories. "
    "On each trial you search one of two hiding spots for a coin. "
    "Each creature has its own favorite hiding spots, which stay stable throughout its block, "
    "but a creature does not always hide its coin in its favorite spot. "
    "Every new creature has different favorite spots, so the odds reset at each new block."
)

BLOCK_LINE = (
    "\nBlock: a new creature hides coins in a new territory. "
    "Its favorite hiding spots are unknown to you.\n"
)

MEMORY_INTRO = (
    "\nSurprise memory test: each of the ten creatures appears one at a time, "
    "and you must recall which of its hiding spots was its favorite. "
    "Five spots are shown at once, labeled A, B, C, D and E in the order they appear. "
    "Press the letter of the spot you think was the creature's favorite.\n"
)

# The 27-image pool from the task (used to name hiding spots in the memory test).
ALL_IMAGES = [
    "1_antHill.jpeg", "1_appleTree.jpeg", "1_barn.jpeg", "1_birdNest.jpeg",
    "1_bridge.jpeg", "1_cabin.jpeg", "1_campfire.jpeg", "1_carrots.jpeg",
    "1_cattail.jpeg", "1_cave.jpeg", "1_cherryBlossom.jpeg", "1_corn.jpeg",
    "1_fort.jpeg", "1_hay.jpeg", "1_iris.jpeg", "1_leaves.jpeg", "1_log.jpeg",
    "1_mossRock.jpeg", "1_mushroom.jpeg", "1_pumpkinCluster.jpeg", "1_rockPile.jpeg",
    "1_treeDoor.jpeg", "1_vines.jpeg", "1_watermelon.jpeg", "1_well.jpeg",
    "1_windmill.jpeg", "1_yellowTree.jpeg",
]


def _img_name(fn):
    """Mirror build_jsonl._img_name: strip the 'N_' prefix and underscores."""
    import re
    m = re.match(r"^\d+_(.+)\.jpe?g$", str(fn))
    if m:
        return m.group(1).replace("_", " ")
    return str(fn)


class NoveltyExploration:
    """Novelty/uncertainty exploration task, Nussenbaum et al. (2023), eLife 12:e84260.

    Design (Materials and methods -> task design; also the shipped jsPsych port
    ``experiments/exp0/index.html``): 10 blocks (creatures/territories) of 15
    free choices. Each block has a 3-spot pool; reward probability of each of the
    three spots is re-randomized per block by shuffling either EASY
    {.2, .5, .8} or HARD {.3, .5, .7}. Blocks 2,3,6,7,10 (1-indexed) are HARD,
    the rest EASY. Block 1 presents 3 novel spots; blocks 2..10 present 2
    familiar (seen before) + 1 novel spot. A "holdout" spot (per a fixed
    schedule) is withheld until its introduction trial. Outcomes follow a
    per-spot win schedule with exactly round(15 * p) winning trials.

    ASSUMPTION: exposure novelty is tracked by "offered > 2 times" as familiar
    (the shipped port tracks a threshold; the precise cutoff only affects which
    spots are labelled novel, not the reward structure or transcript).
    ASSUMPTION: no response-timeouts are simulated; the agent always answers
    (the ~0.5% real "fail to respond" rows are dropped by design of a text
    simulator).

    The DataFrame matches exp0.csv minus ``rt`` and demographic / age-related
    columns (age, gender, iq, WASI_*, nativeEnglish).
    """

    def __init__(self):
        self.name = "nussenbaum_2023_novelty_exp0"
        self.num_blocks = 10
        self.num_trials = 15
        self.num_stims = 12
        self.reward_easy = [0.2, 0.5, 0.8]
        self.reward_hard = [0.3, 0.5, 0.7]
        self.hard_blocks = {1, 2, 5, 6, 9}  # 0-indexed
        # per block: (novelHoldout, famHoldout) trial (1-indexed); 0 = none.
        self.holdout = [
            (0, 0),  # block 0
            (0, 7),  # block 1: familiar holdout on trial 7
            (7, 0),  # block 2: novel   holdout on trial 7
            (0, 13), # block 3
            (15, 0), # block 4
            (0, 11), # block 5
            (12, 0), # block 6
            (0, 9),  # block 7
            (10, 0), # block 8
            (0, 15), # block 9
        ]

    # ------------------------------------------------------------------ #
    # Generative design helpers (port of buildBlock.m via experiments/exp0)
    # ------------------------------------------------------------------ #
    def _build_blocks(self, stim_images):
        """Return 10 dicts describing each block's 3-spot pool, reward probs,
        and per-trial presented pairs. ``stim_images``: list of 12 filenames."""
        num_expose = [0] * self.num_stims
        blocks = []
        for b in range(self.num_blocks):
            novel_hold, fam_hold = self.holdout[b]
            novel_cand = [s for s in range(self.num_stims) if num_expose[s] == 0]
            fam_cand = [s for s in range(self.num_stims) if num_expose[s] > 2]
            if b == 0:
                novel = list(np.random.choice(novel_cand, 3, replace=False))
                fam = []
            else:
                novel = list(np.random.choice(novel_cand, 1, replace=False))
                fam = list(np.random.choice(fam_cand, 2, replace=False))
            block_stims = novel + fam

            probs = list(self.reward_hard if b in self.hard_blocks else self.reward_easy)
            np.random.shuffle(probs)
            p_win = [0.0] * self.num_stims
            for s, p in zip(block_stims, probs):
                p_win[s] = p
            high = next(s for s in block_stims if p_win[s] >= 0.7)
            med = next(s for s in block_stims if p_win[s] == 0.5)
            low = next(s for s in block_stims if p_win[s] <= 0.3)

            # per-spot win schedule across the block's trials
            is_win = {}
            for s in block_stims:
                n_wins = int(np.floor(15 * p_win[s] + 0.5))  # JS Math.round
                win_trials = set(np.random.choice(15, n_wins, replace=False))
                is_win[s] = [int(t in win_trials) for t in range(self.num_trials)]

            # holdout spot and its introduction trial
            hold_stim, hold_trial = None, 0
            if novel_hold > 0:
                hold_stim, hold_trial = novel[0], novel_hold
            elif fam_hold > 0:
                hold_stim, hold_trial = fam[0], fam_hold

            available = set(block_stims)
            if hold_stim is not None:
                available.discard(hold_stim)
            trial_stims = []
            for t in range(self.num_trials):
                if hold_stim is not None and t + 1 == hold_trial:
                    pair = [hold_stim]
                    other = np.random.choice(list(available), 1, replace=False)
                    pair.append(int(other[0]))
                    available.add(hold_stim)
                else:
                    pair = list(np.random.choice(list(available), 2, replace=False))
                np.random.shuffle(pair)
                trial_stims.append(pair)

            for t in range(self.num_trials):
                num_expose[trial_stims[t][0]] += 1
                num_expose[trial_stims[t][1]] += 1

            blocks.append({
                "hard": b in self.hard_blocks,
                "stims": block_stims,
                "p_win": p_win, "high": high, "med": med, "low": low,
                "is_win": is_win, "trial_stims": trial_stims,
            })
        return blocks

    def _reward_probs(self, block):
        """reward_probs_1..12 for a block = empirical wins over first 14 trials."""
        row = [0.0] * self.num_stims
        for s in block["stims"]:
            row[s] = sum(block["is_win"][s][: self.num_trials - 1]) / (self.num_trials - 1)
        return row

    def _build_memory(self, blocks, stim_images, never_seen):
        """Build the 10 memory probes in probe order (interleaved halves)."""
        first = list(range(5))
        second = list(range(5, 10))
        np.random.shuffle(first)
        np.random.shuffle(second)
        order = []
        for i in range(5):
            if np.random.rand() < 0.5:
                order += [first[i], second[i]]
            else:
                order += [second[i], first[i]]
        new_pool = list(never_seen)
        np.random.shuffle(new_pool)
        probes = []
        for probe_idx, block_idx in enumerate(order):
            b = blocks[block_idx]
            stims = set(b["stims"])
            cand = []
            for o in range(1, self.num_blocks):
                other = blocks[(block_idx + o) % self.num_blocks]
                if other["high"] not in stims:
                    cand.append(other["high"])
            high_diff = int(np.random.choice(cand, 1)[0]) if cand else None
            perm = np.random.permutation(5) + 1  # imageOrder_1..5 = type per position
            probes.append({
                "block_idx": block_idx,
                "perm": perm,
                "high_img": stim_images[b["high"]],
                "med_img": stim_images[b["med"]],
                "low_img": stim_images[b["low"]],
                "diff_img": stim_images[high_diff] if high_diff is not None else None,
                "new_img": new_pool[probe_idx % len(new_pool)],
            })
        return probes

    # ------------------------------------------------------------------ #
    # Simulation
    # ------------------------------------------------------------------ #
    def simulate(self, agent, num_simulations, max_chars=None):
        columns = [
            "participant_id", "task_id", "trial", "response", "reward", "valid",
            "phase", "blockID", "block_difficulty", "choice_set", "correct", "explorationBlock",
            "exposureHistory_b_1", "exposureHistory_b_2",
            "exposureHistory_t_1", "exposureHistory_t_2",
            "highRewDiffImage", "highRewImage",
            "imageOrder_1", "imageOrder_2", "imageOrder_3", "imageOrder_4",
            "imageOrder_5", "lossHistory_b_1", "lossHistory_b_2",
            "lossHistory_t_1", "lossHistory_t_2", "lowRewImage", "medRewImage",
            "memData", "newImage", "numBlockStims",
            "rejectHistory_b_1", "rejectHistory_b_2",
            "rejectHistory_t_1", "rejectHistory_t_2", "rejectedStimID",
            "reward_probs_1", "reward_probs_2", "reward_probs_3", "reward_probs_4",
            "reward_probs_5", "reward_probs_6", "reward_probs_7", "reward_probs_8",
            "reward_probs_9", "reward_probs_10", "reward_probs_11", "reward_probs_12",
            "selectHistory_b_1", "selectHistory_b_2",
            "selectHistory_t_1", "selectHistory_t_2", "selectedStimID",
            "trialID", "trialStimID_1", "trialStimID_2",
            "winHistory_b_1", "winHistory_b_2",
            "winHistory_t_1", "winHistory_t_2",
        ]
        rows = []
        prompts = []
        for participant in tqdm(range(num_simulations)):
            stim_images = list(np.random.choice(ALL_IMAGES, self.num_stims, replace=False))
            never_seen = [x for x in ALL_IMAGES if x not in stim_images]
            blocks = self._build_blocks(stim_images)
            mem_probes = self._build_memory(blocks, stim_images, never_seen)

            prompt = INSTRUCTIONS + "\n"

            # ---- exploration blocks ----
            for b in range(self.num_blocks):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                prompt += BLOCK_LINE
                blk = blocks[b]
                # per-block histograms: sel/rej/win/loss/exp by stim id
                hist = {"sel": [0] * self.num_stims, "rej": [0] * self.num_stims,
                        "win": [0] * self.num_stims, "loss": [0] * self.num_stims,
                        "exp": [0] * self.num_stims}
                hist_task = {"sel": [0] * self.num_stims, "rej": [0] * self.num_stims,
                             "win": [0] * self.num_stims, "loss": [0] * self.num_stims,
                             "exp": [0] * self.num_stims}
                for t in range(self.num_trials):
                    sa, sb = blk["trial_stims"][t]
                    prompt += (f"You see {_img_name(stim_images[sa])} and {_img_name(stim_images[sb])} "
                               f"(A = the first spot, B = the second). You press "
                               f"[HUMAN_RESPONSE]")
                    tok = agent(prompt, choice_options=["A", "B"])
                    response = 0 if tok == "A" else 1
                    selected = sa if response == 0 else sb
                    rejected = sb if response == 0 else sa
                    reward = blk["is_win"][selected][t]
                    prompt += (f"{tok}[/HUMAN_RESPONSE]. "
                               + ("You find a coin." if reward == 1 else "You do not find a coin.")
                               + "\n")

                    # numBlockStims = distinct spots offered up to & incl. this trial
                    offered = set()
                    for tt in range(t + 1):
                        offered.add(blk["trial_stims"][tt][0])
                        offered.add(blk["trial_stims"][tt][1])

                    row = {
                        "participant_id": participant, "task_id": b, "trial": t,
                        "response": float(response), "reward": float(reward),
                        "valid": 1, "phase": "exploration",
                        "blockID": float(b + 1),
                        "block_difficulty": float(1 if blk["hard"] else 0),
                        "choice_set": json.dumps([stim_images[sa], stim_images[sb]]),
                        "correct": np.nan, "explorationBlock": np.nan,
                        "exposureHistory_b_1": float(hist["exp"][sa]),
                        "exposureHistory_b_2": float(hist["exp"][sb]),
                        "exposureHistory_t_1": float(hist_task["exp"][sa]),
                        "exposureHistory_t_2": float(hist_task["exp"][sb]),
                        "highRewDiffImage": np.nan, "highRewImage": np.nan,
                        "imageOrder_1": np.nan, "imageOrder_2": np.nan,
                        "imageOrder_3": np.nan, "imageOrder_4": np.nan,
                        "imageOrder_5": np.nan,
                        "lossHistory_b_1": float(hist["loss"][sa]),
                        "lossHistory_b_2": float(hist["loss"][sb]),
                        "lossHistory_t_1": float(hist_task["loss"][sa]),
                        "lossHistory_t_2": float(hist_task["loss"][sb]),
                        "lowRewImage": np.nan, "medRewImage": np.nan,
                        "memData": 1, "newImage": np.nan,
                        "numBlockStims": float(len(offered)),
                        "rejectHistory_b_1": float(hist["rej"][sa]),
                        "rejectHistory_b_2": float(hist["rej"][sb]),
                        "rejectHistory_t_1": float(hist_task["rej"][sa]),
                        "rejectHistory_t_2": float(hist_task["rej"][sb]),
                        "rejectedStimID": float(rejected + 1),
                        "selectedStimID": float(selected + 1),
                        "trialID": float(t + 1),
                        "trialStimID_1": float(sa + 1),
                        "trialStimID_2": float(sb + 1),
                        "selectHistory_b_1": float(hist["sel"][sa]),
                        "selectHistory_b_2": float(hist["sel"][sb]),
                        "selectHistory_t_1": float(hist_task["sel"][sa]),
                        "selectHistory_t_2": float(hist_task["sel"][sb]),
                        "winHistory_b_1": float(hist["win"][sa]),
                        "winHistory_b_2": float(hist["win"][sb]),
                        "winHistory_t_1": float(hist_task["win"][sa]),
                        "winHistory_t_2": float(hist_task["win"][sb]),
                    }
                    for i, v in enumerate(self._reward_probs(blk), start=1):
                        row[f"reward_probs_{i}"] = v
                    rows.append(row)

                    # update histograms AFTER logging (cumsum up to current trial)
                    hist["sel"][selected] += 1
                    hist["rej"][rejected] += 1
                    hist["exp"][sa] += 1
                    hist["exp"][sb] += 1
                    if reward == 1:
                        hist["win"][selected] += 1
                    else:
                        hist["loss"][selected] += 1
                    hist_task["sel"][selected] += 1
                    hist_task["rej"][rejected] += 1
                    hist_task["exp"][sa] += 1
                    hist_task["exp"][sb] += 1
                    if reward == 1:
                        hist_task["win"][selected] += 1
                    else:
                        hist_task["loss"][selected] += 1

            # ---- surprise memory test ----
            if max_chars is not None and len(prompt) >= max_chars:
                prompts.append(prompt)
                continue
            prompt += MEMORY_INTRO
            for probe_idx, probe in enumerate(mem_probes):
                blk = blocks[probe["block_idx"]]
                pos_to_type = {k: int(probe["perm"][k - 1]) for k in range(1, 6)}
                type_to_img = {
                    1: probe["high_img"], 2: probe["med_img"], 3: probe["low_img"],
                    4: probe["diff_img"], 5: probe["new_img"],
                }
                names = [_img_name(type_to_img[pos_to_type[pos]]) for pos in range(1, 6)]
                prompt += (f"Creature from territory {probe['block_idx'] + 1}: "
                           f"five hiding spots shown, "
                           f"{', '.join(f'{l} = {n}' for l, n in zip('ABCDE', names))}. "
                           f"You press [HUMAN_RESPONSE]")
                tok = self._agent_letter(prompt, agent)
                resp = "ABCDE".index(tok)  # 0-indexed array position, as in exp0.csv
                prompt += f"{tok}[/HUMAN_RESPONSE].\n"

                correct = 1 if pos_to_type[resp + 1] == 1 else 0
                row = {
                    "participant_id": participant, "task_id": 10, "trial": probe_idx,
                    "response": float(resp), "reward": np.nan, "valid": 1,
                    "phase": "memory", "blockID": np.nan,
                    "block_difficulty": np.nan,
                    "choice_set": json.dumps([type_to_img[pos_to_type[pos]] for pos in range(1, 6)]),
                    "correct": float(correct),
                    "explorationBlock": float(probe["block_idx"] + 1),
                    "exposureHistory_b_1": np.nan, "exposureHistory_b_2": np.nan,
                    "exposureHistory_t_1": np.nan, "exposureHistory_t_2": np.nan,
                    "highRewDiffImage": probe["diff_img"], "highRewImage": probe["high_img"],
                    "imageOrder_1": float(probe["perm"][0]),
                    "imageOrder_2": float(probe["perm"][1]),
                    "imageOrder_3": float(probe["perm"][2]),
                    "imageOrder_4": float(probe["perm"][3]),
                    "imageOrder_5": float(probe["perm"][4]),
                    "lossHistory_b_1": np.nan, "lossHistory_b_2": np.nan,
                    "lossHistory_t_1": np.nan, "lossHistory_t_2": np.nan,
                    "lowRewImage": probe["low_img"], "medRewImage": probe["med_img"],
                    "memData": 1, "newImage": probe["new_img"],
                    "numBlockStims": np.nan,
                    "rejectHistory_b_1": np.nan, "rejectHistory_b_2": np.nan,
                    "rejectHistory_t_1": np.nan, "rejectHistory_t_2": np.nan,
                    "rejectedStimID": np.nan, "selectedStimID": np.nan,
                    "trialID": np.nan, "trialStimID_1": np.nan, "trialStimID_2": np.nan,
                    "selectHistory_b_1": np.nan, "selectHistory_b_2": np.nan,
                    "selectHistory_t_1": np.nan, "selectHistory_t_2": np.nan,
                    "winHistory_b_1": np.nan, "winHistory_b_2": np.nan,
                    "winHistory_t_1": np.nan, "winHistory_t_2": np.nan,
                }
                for i in range(1, 13):
                    row[f"reward_probs_{i}"] = np.nan
                rows.append(row)

            prompts.append(prompt.strip())

        df = pd.DataFrame(rows, columns=columns)
        for c in ["reward_probs_" + str(i) for i in range(1, 13)]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        return df, prompts

    @staticmethod
    def _agent_letter(prompt, agent, choice_options=("A", "B", "C", "D", "E")):
        tok = agent(prompt, choice_options=list(choice_options))
        if tok not in choice_options:
            tok = np.random.choice(list(choice_options))
        return tok


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

    task = NoveltyExploration()
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