# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp3 (Experiment 4) of ``Hugging-Brain/chambon_2020_information``,
format-identical to the repo's ``transcripts3.jsonl``.

``uv run simulate3.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import zlib

import numpy as np
import pandas as pd
from tqdm import tqdm

LETTER_POOLS = [("X", "Y"), ("P", "Q"), ("R", "S"), ("M", "N"), ("K", "L"),
                ("E", "F"), ("T", "V"), ("B", "C"), ("G", "H"), ("A", "Z"),
                ("D", "W"), ("J", "U")]


def _letters(pid):
    """One fixed letter pair per participant (named in pool order); which letter names
    the best-rewarded symbol is randomized per participant."""
    h = zlib.crc32(f"{pid}".encode("utf-8"))
    l1, l2 = LETTER_POOLS[h % len(LETTER_POOLS)]
    if (h // len(LETTER_POOLS)) % 2 == 0:
        return l1, l2, l1, l2          # best_letter=l1, least_letter=l2
    return l1, l2, l2, l1              # best_letter=l2, least_letter=l1


def _outcome_txt(v):
    if np.isnan(v):
        return ""
    return "You win a point." if v == 1 else "You lose a point."


def _intro(l1, l2, forced_present, confirm):
    t = ("Your task is to learn which of the two symbols in front of you is more "
         "rewarding. Each symbol has a hidden, fixed probability of winning you a "
         "point (+1) or losing you a point (-1) that stays the same for a whole "
         "block; at the start of each block a fresh pair of symbols is used, so the "
         "hidden probabilities can differ between blocks. In every block the two "
         f"symbols are called {l1} and {l2}. On each trial the block's two symbols "
         f"are shown, and you choose one by typing its single-letter name ({l1} or "
         f"{l2}). After your choice the outcome is revealed.")
    if forced_present:
        t += (" On some trials the choice is imposed rather than free: you are "
              "instructed to take a specified symbol, and you must take it; the "
              "outcome of an imposed trial is shown to you but is not added to your "
              "points.")
    if confirm:
        t += " After each outcome you press the confirm key, and then the next trial begins."
    return t


def _intro_exp3():
    return ("In this experiment you take a symbol either by pressing the response key "
            "or by not pressing it: on every trial one of the two symbols is taken by "
            "pressing the key within 1.5 seconds, and the other is taken by making no "
            "key press. Which symbol goes with the key press is stated on every trial.")


class GoNoGoBandit:
    """Probabilistic two-symbol learning task, Experiment 4 of Chambon et al.
    (2020), "Information about action outcomes differentially affects learning
    from self-determined versus imposed choices", Nature Human Behaviour, 4,
    1067-1079. Design: Methods, 'Conditions' and 'Trial structure' (p. 1077) —
    six blocks of 100 free-choice trials; on every trial the two symbols are
    shown at the top and bottom of the screen (pseudo-random), a key press
    within 1,500 ms takes the symbol at the participant's instructed position
    (go), and no key press takes the other symbol (no-go); whether a trial is
    go or no-go is therefore the participant's own choice, not a cue. Reward
    contingencies as in Experiment 3: random 50/50 blocks (condition 1) and
    instrumental 70/30 blocks (condition 2), recovered from the data's outcome
    rates.

    The narration mirrors build_jsonl.py exactly: one letter pair per
    participant, best letter randomized per participant, the per-trial
    statement of which symbol the key press takes, the free symbol pick
    wrapped in [HUMAN_RESPONSE], and the chosen symbol's +1/-1 outcome.

    ASSUMPTION: the best symbol sits on the key-press side on a random half
    of the trials (the data's best_side is balanced); the key-press side code
    is +1 for every simulated participant (build_jsonl.py recovers it from the
    go trials). rt is filled with random millisecond values below the 1,500 ms
    deadline on go trials and at the deadline on no-go trials.
    """

    def __init__(self):
        self.name = "chambon_2020_information_exp3"
        self.num_subjects = 17
        self.press_side = 1            # +/-1 side code that a key press selects
        self.sessions = [1, 2, 3]
        # (condition index, prob_best, prob_least, n_trials per block)
        self.tasks = [
            (0, 0.5, 0.5, 100),
            (1, 0.7, 0.3, 100),
        ]

    def simulate(self, agent, num_simulations, max_chars=None):
        all_rows, prompts = [], []
        for p in tqdm(range(num_simulations)):
            pid = f"P{p:03d}"
            subject = p + 1
            l1, l2, best_letter, least_letter = _letters(pid)
            prompt = _intro(l1, l2, forced_present=False, confirm=False) + "\n"
            prompt += _intro_exp3() + "\n"
            rows = []
            block = 0
            stop = False
            for session in self.sessions:
                for k in np.random.permutation(len(self.tasks)):
                    cond, p_best, p_least, n_trials = self.tasks[k]
                    if max_chars is not None and len(prompt) >= max_chars:
                        stop = True
                        break
                    condition_code = cond + 1
                    prompt += (f"Block begins (Session {session}): a fresh pair of "
                               f"symbols, called {l1} and {l2}.\n")
                    for t_in_block in range(1, n_trials + 1):
                        best_side = self.press_side if np.random.rand() < 0.5 else -self.press_side
                        press = best_letter if best_side == self.press_side else least_letter
                        nopress = least_letter if press == best_letter else best_letter
                        o_best = 1 if np.random.rand() < p_best else -1
                        o_least = 1 if np.random.rand() < p_least else -1
                        head = (f"Symbols {l1} and {l2} shown; pressing the key takes {press}, "
                                f"not pressing takes {nopress}. You take [HUMAN_RESPONSE]")
                        letter = agent(prompt + head, choice_options=[l1, l2])
                        response = 1 if letter == best_letter else 0
                        chosen = best_letter if response == 1 else least_letter
                        chosen_side = best_side if response == 1 else -best_side
                        go = 1 if chosen_side == self.press_side else 0
                        ch_out = o_best if response == 1 else o_least
                        prompt += head + f"{chosen}[/HUMAN_RESPONSE]. " + _outcome_txt(ch_out) + "\n"
                        rows.append({
                            "participant_id": pid, "subject_number": subject,
                            "session": session, "condition_code": condition_code,
                            "trial_in_block": t_in_block, "outcome_best": o_best,
                            "outcome_least": o_least, "response": response,
                            "chosen_side": chosen_side,
                            "rt": round(float(np.random.uniform(200, 1400)), 1) if go
                                  else round(float(1500 + np.random.uniform(0, 15)), 1),
                            "go": go, "nogo": 1 - go, "best_side": best_side,
                            "task_id": block, "trial": t_in_block - 1,
                        })
                    block += 1
                if stop:
                    break
            prompts.append(prompt.strip())
            all_rows.append(pd.DataFrame(rows))
        df = pd.concat(all_rows, ignore_index=True)
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

    task = GoNoGoBandit()
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
