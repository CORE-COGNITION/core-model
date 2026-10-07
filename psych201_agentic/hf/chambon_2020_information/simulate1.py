# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 (Experiment 2) of ``Hugging-Brain/chambon_2020_information``,
format-identical to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
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

CF_BLOCKS = {2, 4}  # condition_code with counterfactual (forgone) outcome shown


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


def _cf_txt(v):
    if np.isnan(v):
        return ""
    return " The unchosen symbol would have won a point." if v == 1 else \
        " The unchosen symbol would have lost a point."


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
    """Probabilistic two-symbol learning task, Experiment 2 of Chambon et al.
    (2020), "Information about action outcomes differentially affects learning
    from self-determined versus imposed choices", Nature Human Behaviour, 4,
    1067-1079. Design: Methods, 'Conditions' (p. 1077) — free- and forced-choice
    trials are intermixed in all four conditions; conditions 1 & 2 are
    high-reward (better symbol 90%, other 60%), conditions 3 & 4 low-reward
    (40% / 10%); conditions 1 & 3 show only the factual (chosen) outcome,
    conditions 2 & 4 show both factual and counterfactual (forgone) outcomes,
    on free and forced trials alike.

    The narration mirrors build_jsonl.py exactly: one letter pair per
    participant, best letter randomized per participant, [HUMAN_RESPONSE]
    markers on free choices only, blocks in presentation order, and the
    forgone-outcome sentence added whenever condition_code in {2, 4}.

    Simulated participants draw rewards from the paper's 90/60 and 40/10
    contingencies; the forced-trial schedule is 50% of trials, forced-to-best
    half the time (data-verified).

    ASSUMPTION: the data group the 16 blocks into 4 sessions, each holding one
    block per condition in a random order; the simulator follows that layout.
    ASSUMPTION: rt and rt_confirm are uninformative reaction-time columns a
    text simulator cannot produce meaningfully, so they are filled with random
    positive millisecond values (rt_confirm is required by build_jsonl.py to
    add the 'press to confirm' phrase).
    """

    def __init__(self):
        self.name = "chambon_2020_information_exp1"
        self.num_subjects = 24
        self.forced_rate = 0.5         # forced trials within every block
        self.forced_best_rate = 0.5    # forced to the best symbol half the time
        self.sessions = [1, 2, 3, 4]
        # (condition index, prob_best, prob_least, n_trials per block)
        self.tasks = [
            (0, 0.9, 0.6, 40),
            (1, 0.9, 0.6, 40),
            (2, 0.4, 0.1, 40),
            (3, 0.4, 0.1, 40),
        ]

    def simulate(self, agent, num_simulations, max_chars=None):
        all_rows, prompts = [], []
        for p in tqdm(range(num_simulations)):
            pid = f"P{p:03d}"
            subject = p + 1
            l1, l2, best_letter, least_letter = _letters(pid)
            prompt = _intro(l1, l2, forced_present=True, confirm=True) + "\n"
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
                    cf = condition_code in CF_BLOCKS
                    extra = (" In this block both the chosen and the unchosen symbols' "
                             "outcomes are shown.") if cf else ""
                    prompt += (f"Block begins (Session {session}): a fresh pair of "
                               f"symbols, called {l1} and {l2}.{extra}\n")
                    for t_in_block in range(1, n_trials + 1):
                        forced = np.random.rand() < self.forced_rate
                        response, o_best, o_least = self._trial_values(
                            p_best, p_least, forced, l1, l2, best_letter, agent, prompt)
                        prompt += self._trial_line(l1, l2, best_letter, least_letter,
                                                   response, o_best, o_least, forced, cf)
                        rows.append({
                            "participant_id": pid, "subject_number": subject,
                            "session": session, "condition_code": condition_code,
                            "trial_in_block": t_in_block, "outcome_best": o_best,
                            "outcome_least": o_least, "response": response,
                            "forced_choice": 1 if forced else 0,
                            "rt": round(float(np.random.uniform(400, 2500)), 1),
                            "rt_confirm": round(float(np.random.uniform(300, 2000)), 1),
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

    def _trial_line(self, l1, l2, best_letter, least_letter, response, o_best, o_least,
                    forced, cf):
        chosen = best_letter if response == 1 else least_letter
        ch_out = o_best if response == 1 else o_least
        other_out = o_least if response == 1 else o_best
        if forced:
            line = f"You are instructed to take {chosen}. " + _forced_outcome_txt(chosen, ch_out)
        else:
            line = (f"Symbols {l1} and {l2} shown. "
                    f"You press [HUMAN_RESPONSE]{chosen}[/HUMAN_RESPONSE]. "
                    + _outcome_txt(ch_out))
        if cf:
            line += _cf_txt(other_out)
        line += " You press to confirm."
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
