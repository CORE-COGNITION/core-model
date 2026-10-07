# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp2 (Experiment 3) of ``Hugging-Brain/chambon_2020_information``,
format-identical to the repo's ``transcripts2.jsonl``.

``uv run simulate2.py -n 3`` smoke-tests with a uniform-random agent; or import
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


def _forced_outcome_txt(letter, v):
    if np.isnan(v):
        return ""
    return f"{letter} wins a point." if v == 1 else f"{letter} loses a point."


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


class TwoSymbolLearningTask:
    """Probabilistic two-symbol learning task, Experiment 3 of Chambon et al.
    (2020), "Information about action outcomes differentially affects learning
    from self-determined versus imposed choices", Nature Human Behaviour, 4,
    1067-1079. Design: Methods, 'Conditions' (p. 1077) — free-choice blocks of
    20 trials and intermixed free/forced blocks of 40 trials; half the blocks
    use a random reward schedule (both symbols win 50%), the other half are
    instrumental (one symbol wins 70%, the other 30%).

    The narration mirrors build_jsonl.py exactly: one letter pair per
    participant, best letter randomized per participant, [HUMAN_RESPONSE]
    markers on free choices only, blocks in presentation order.

    ASSUMPTION: the condition-to-schedule assignment is recovered from the
    data's outcome rates: conditions 1 & 2 (task_id 0, 1) are the random 50/50
    schedule, conditions 3 & 4 (task_id 2, 3) the instrumental 70/30 schedule;
    conditions 1 & 3 are free-choice-only blocks of 20 trials, 2 & 4 intermixed
    blocks of 40 trials (50% forced, forced-to-best half the time).
    ASSUMPTION: the data spread the 12 blocks over 3 sessions unevenly across
    participants; the simulator uses one block per condition per session in a
    random order.
    ASSUMPTION: rt is an uninformative reaction-time column a text simulator
    cannot produce meaningfully, so it is filled with random positive
    millisecond values; this experiment records no rt_confirm.
    """

    def __init__(self):
        self.name = "chambon_2020_information_exp2"
        self.num_subjects = 30
        self.forced_rate = 0.5         # forced trials within intermixed blocks
        self.forced_best_rate = 0.5    # forced to the best symbol half the time
        self.sessions = [1, 2, 3]
        # (condition index, prob_best, prob_least, forced, n_trials per block)
        self.tasks = [
            (0, 0.5, 0.5, False, 20),
            (1, 0.5, 0.5, True, 40),
            (2, 0.7, 0.3, False, 20),
            (3, 0.7, 0.3, True, 40),
        ]

    def simulate(self, agent, num_simulations, max_chars=None):
        all_rows, prompts = [], []
        for p in tqdm(range(num_simulations)):
            pid = f"P{p:03d}"
            subject = p + 1
            l1, l2, best_letter, least_letter = _letters(pid)
            prompt = _intro(l1, l2, forced_present=True, confirm=False) + "\n"
            rows = []
            block = 0
            stop = False
            for session in self.sessions:
                for k in np.random.permutation(len(self.tasks)):
                    cond, p_best, p_least, forced_allowed, n_trials = self.tasks[k]
                    if max_chars is not None and len(prompt) >= max_chars:
                        stop = True
                        break
                    condition_code = cond + 1
                    prompt += (f"Block begins (Session {session}): a fresh pair of "
                               f"symbols, called {l1} and {l2}.\n")
                    for t_in_block in range(1, n_trials + 1):
                        forced = forced_allowed and np.random.rand() < self.forced_rate
                        response, o_best, o_least = self._trial_values(
                            p_best, p_least, forced, l1, l2, best_letter, agent, prompt)
                        prompt += self._trial_line(l1, l2, best_letter, least_letter,
                                                   response, o_best, o_least, forced)
                        rows.append({
                            "participant_id": pid, "subject_number": subject,
                            "session": session, "condition_code": condition_code,
                            "trial_in_block": t_in_block, "outcome_best": o_best,
                            "outcome_least": o_least, "response": response,
                            "forced_choice": 1 if forced else 0,
                            "rt": round(float(np.random.uniform(400, 2500)), 1),
                            "task_id": block, "trial": t_in_block - 1,
                        })
                    block += 1
                if stop:
                    break
            prompts.append(prompt.strip())
            all_rows.append(pd.DataFrame(rows))
        df = pd.concat(all_rows, ignore_index=True)
        return df, prompts

    def _trial_values(self, p_best, p_least, forced, l1, l2, best_letter, agent, prompt):
        # both outcomes are drawn on every trial (the source records both)
        o_best = 1 if np.random.rand() < p_best else -1
        o_least = 1 if np.random.rand() < p_least else -1
        if forced:
            return (1 if np.random.rand() < self.forced_best_rate else 0), o_best, o_least
        cue = prompt + f"Symbols {l1} and {l2} shown. You press [HUMAN_RESPONSE]"
        letter = agent(cue, choice_options=[l1, l2])
        return (1 if letter == best_letter else 0), o_best, o_least

    def _trial_line(self, l1, l2, best_letter, least_letter, response, o_best, o_least, forced):
        chosen = best_letter if response == 1 else least_letter
        ch_out = o_best if response == 1 else o_least
        if forced:
            line = f"You are instructed to take {chosen}. " + _forced_outcome_txt(chosen, ch_out)
        else:
            line = (f"Symbols {l1} and {l2} shown. "
                    f"You press [HUMAN_RESPONSE]{chosen}[/HUMAN_RESPONSE]. "
                    + _outcome_txt(ch_out))
        return line + "\n"


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

    task = TwoSymbolLearningTask()
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
