# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 of ``Hugging-Brain/bavard_2018_referencepoint``,
format-identical to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import json
import random

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp1 + instruction constants).
INSTR_LEARN_COMMON = (
    "You are taking part in an experiment in which you can win or lose money. "
    "Your goal is to maximize your payoff: seeking monetary rewards and avoiding "
    "monetary losses are equally important.\n"
    "On each trial you see two abstract symbols, one on the left and one on the right "
    "of a central fixation cross. Each symbol is associated with a chance of producing "
    "a monetary outcome, and your task is to learn, from the outcomes you receive, which "
    "symbol is more advantageous and to choose it.\n"
    "To make your choice, press the button that matches the side of the chosen symbol "
    "(leftmost or rightmost) within 3 seconds. A red pointer then marks your selection "
    "and the outcome of the chosen symbol is shown: '+1.0€', '+0.1€', '0.0€', '-0.1€' or "
    "'-1.0€'.\n"
    "In this transcript every symbol has a label, and your choice is recorded as the label "
    "of the symbol you selected.\n"
)

PARTIAL_INSTR = (
    "\nIn this second version of the experiment, some trials give 'complete' feedback: "
    "after your choice you see the outcomes of BOTH the chosen symbol and the other, "
    "unchosen symbol. In the other, 'partial' trials, you only see the outcome of the "
    "chosen symbol.\n"
)

S1_INSTR = (
    "Session 1 uses four pairs of symbols, which are labeled as follows in this transcript:\n"
    "- reward/big pair: Symbol A and Symbol B\n"
    "- reward/small pair: Symbol C and Symbol D\n"
    "- loss/big pair: Symbol E and Symbol F\n"
    "- loss/small pair: Symbol G and Symbol H\n"
    "When you make a choice, type the label (A, B, C, D, E, F, G or H) of the symbol you choose.\n"
)

S2_INSTR = (
    "Session 2 uses four new pairs of symbols, numbered 1 to 8 in this transcript:\n"
    "- reward/big pair: Symbol 1 and Symbol 2\n"
    "- reward/small pair: Symbol 3 and Symbol 4\n"
    "- loss/big pair: Symbol 5 and Symbol 6\n"
    "- loss/small pair: Symbol 7 and Symbol 8\n"
    "When you make a choice, type the number (1, 2, 3, 4, 5, 6, 7 or 8) of the symbol you choose.\n"
)

TRANSFER_INSTR = (
    "After the two learning sessions you perform a transfer test of 112 trials.\n"
    "In each trial you again see two of the eight symbols of Session 2 (Symbols 1 to 8), "
    "possibly in a combination you have never seen together before. There is no feedback: "
    "you simply indicate which of the two symbols you believe has the higher value by typing "
    "its number (1 to 8).\n"
)

S1_LETTERS = {1: ("A", "B"), 2: ("C", "D"), 3: ("E", "F"), 4: ("G", "H")}
S2_SYMBOLS = {5: (1, 2), 6: (3, 4), 7: (5, 6), 8: (7, 8)}  # con code -> symbol ids
CTX = {1: ("reward", "big"), 2: ("reward", "small"),
       3: ("loss", "big"), 4: ("loss", "small"),
       5: ("reward", "big"), 6: ("reward", "small"),
       7: ("loss", "big"), 8: ("loss", "small")}
MAG_VALUE = {"big": 1.0, "small": 0.1}


def _s1_fav(pseed, code):
    # Mirror build_jsonl.py: which letter of the fixed pair is favorable is assigned
    # per participant via a deterministic hash of (participant, context_code), since the
    # raw S1 data only codes choices as correct/incorrect.
    rng = random.Random(f"{pseed}-s1-{int(code)}")
    a, b = S1_LETTERS[int(code)]
    return a if rng.random() < 0.5 else b


def _fmt_euro(v):
    if v == 0:
        return "0.0€"
    if v > 0:
        return f"+{v:.1f}€"
    return f"{v:.1f}€"


def _draw_outcome(valence, magnitude, is_fav):
    # Paper (Methods): favorable option yields its magnitude with p=.75 in reward
    # contexts / p=.25 in loss contexts; unfavorable with the complementary p; else 0.
    mag = MAG_VALUE[magnitude]
    if valence == "reward":
        p = 0.75 if is_fav else 0.25
        return float(mag) if np.random.rand() < p else 0.0
    else:
        p = 0.25 if is_fav else 0.75
        return -float(mag) if np.random.rand() < p else 0.0


def _good(valence, reward):
    return 1.0 if (valence == "reward" and reward > 0) or (valence == "loss" and reward == 0) else 0.0


class ReferencePointLearningComplete:
    """Probabilistic instrumental learning task, Exp. 2 of Bavard et al. (2018),
    "Reference-point centering and range-adaptation enhance human reinforcement
    learning at the cost of irrational preferences", Nat. Commun. 9, 4503.

    Design (Methods, Results "Behavioral paradigm"): as Exp. 1 (see
    bavard_2018_referencepoint_exp0) but with a third factor, feedback information:
    half of the learning trials give complete feedback (both chosen and unchosen
    outcomes shown), half give partial feedback (chosen outcome only). Both outcomes
    are drawn every trial (the raw data always carries the counterfactual outcome);
    the transcript narrates the counterfactual only on complete-feedback trials.

    ASSUMPTION: Session-1 favorable letters are not recoverable from the raw data
    (learning responses code correct/incorrect only), so the generator assigns the
    favorable letter per participant via the same deterministic (participant, context)
    hash build_jsonl.py uses. In Session 2 and the transfer test the favorable symbol
    is the first id of each pair (symbols 1,3,5,7), consistent with build_jsonl's
    response coding (response 1 == the pair's first symbol). The per-session context
    order is a uniform permutation of 20 reps of each context, rejection-sampled so no
    run exceeds 4 (matching exp0.csv; exp1.csv has runs up to 6). feedback_info follows
    the raw con3 coding (0 = complete, 1 = partial) and is fixed per cue pair: complete
    feedback for the two big-magnitude pairs in one session and the two small-magnitude
    pairs in the other (contexts {1,3,6,8} or {2,4,5,7}), counterbalanced across
    participants, as in the shipped exp1.csv.

    The DataFrame matches exp1.csv exactly (same columns, dtypes, codings).
    """

    def __init__(self):
        self.name = "bavard_2018_referencepoint_exp1"
        self.trials_per_session = 80
        self.num_contexts = 4
        self.transfer_pairs = 28
        self.transfer_reps = 4

    def _session_order(self):
        while True:
            order = list(range(1, self.num_contexts + 1)) * 20
            random.shuffle(order)
            if self._max_run(order) <= 4:
                return order

    @staticmethod
    def _max_run(seq):
        m, c = 1, 1
        for i in range(1, len(seq)):
            c = c + 1 if seq[i] == seq[i - 1] else 1
            m = max(m, c)
        return m

    def _transfer_order(self):
        # Each unordered pair 4 times, twice in each left/right order (as in the CSVs).
        pairs = [(a, b) for a in range(1, 9) for b in range(a + 1, 9)]
        trials = []
        for rep in range(self.transfer_reps):
            for (a, b) in pairs:
                trials.append((a, b) if rep % 2 == 0 else (b, a))
        random.shuffle(trials)
        return trials

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            prompt = INSTR_LEARN_COMMON.strip() + PARTIAL_INSTR
            # Feedback information is a cue-pair property, counterbalanced across
            # participants (the two patterns in the shipped exp1.csv).
            complete_ctx = {1, 3, 6, 8} if np.random.rand() < 0.5 else {2, 4, 5, 7}
            learning_trial = 0
            for session in (0, 1):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                offset = 0 if session == 0 else 4
                prompt += f"\n--- Session {session + 1} begins. ---"
                prompt += "\n" + (S1_INSTR.strip() if session == 0 else S2_INSTR.strip())
                for code in self._session_order():
                    code_full = code + offset
                    valence, magnitude = CTX[code_full]
                    if session == 0:
                        a, b = S1_LETTERS[code]
                        fav = _s1_fav(participant, code)
                    else:
                        a, b = S2_SYMBOLS[code_full]
                        fav = a
                    prompt += (f"\nThe {valence}/{magnitude} pair (Symbol {a} and "
                               f"Symbol {b}) is presented. You press [HUMAN_RESPONSE]")
                    tok = agent(prompt, choice_options=[a, b])
                    if session == 0:
                        is_fav = tok == fav
                    else:
                        is_fav = int(tok) == fav
                    response = 1 if is_fav else 0
                    reward = _draw_outcome(valence, magnitude, is_fav)
                    cou = _draw_outcome(valence, magnitude, not is_fav)
                    feedback_info = 0.0 if code_full in complete_ctx else 1.0
                    if feedback_info == 0:
                        outcome_txt = (f"The chosen symbol shows {_fmt_euro(reward)}; the "
                                       f"unchosen symbol would have shown {_fmt_euro(cou)}.")
                    else:
                        outcome_txt = f"The chosen symbol shows {_fmt_euro(reward)}."
                    prompt += f"{tok}[/HUMAN_RESPONSE]. {outcome_txt}"
                    rows.append({
                        "participant_id": participant, "task_id": 0, "phase": "learning",
                        "trial": learning_trial, "block": float(session),
                        "context_code": float(code_full), "context": float(code),
                        "valence": valence, "magnitude": magnitude, "cho": float(response + 1),
                        "aa": float("nan"), "response": response, "reward": reward,
                        "outcome_binary": _good(valence, reward),
                        "feedback_info": float(feedback_info),
                        "counterfactual_reward": cou,
                        "counterfactual_binary": _good(valence, cou),
                        "stimulus_left": float("nan"), "stimulus_right": float("nan"),
                        "choice_set": float("nan"),
                    })
                    learning_trial += 1
            if not (max_chars is not None and len(prompt) >= max_chars):
                prompt += "\n" + TRANSFER_INSTR.strip()
                for transfer_trial, (left, right) in enumerate(self._transfer_order()):
                    prompt += (f"\nSymbol {left} and Symbol {right} are shown. "
                               f"You press [HUMAN_RESPONSE]")
                    tok = agent(prompt, choice_options=[left, right])
                    response = 0 if int(tok) == left else 1
                    prompt += f"{tok}[/HUMAN_RESPONSE]."
                    rows.append({
                        "participant_id": participant, "task_id": 1, "phase": "transfer",
                        "trial": transfer_trial, "block": float("nan"),
                        "context_code": float("nan"), "context": float("nan"),
                        "valence": float("nan"), "magnitude": float("nan"),
                        "cho": float("nan"), "aa": float(response + 1), "response": response,
                        "reward": float("nan"), "outcome_binary": float("nan"),
                        "feedback_info": float("nan"), "counterfactual_reward": float("nan"),
                        "counterfactual_binary": float("nan"),
                        "stimulus_left": float(left), "stimulus_right": float(right),
                        "choice_set": json.dumps([left, right]),
                    })
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "task_id", "phase", "trial", "block", "context_code",
            "context", "valence", "magnitude", "cho", "aa", "response", "reward",
            "outcome_binary", "feedback_info", "counterfactual_reward",
            "counterfactual_binary", "stimulus_left", "stimulus_right", "choice_set",
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
        random.seed(args.seed)

    task = ReferencePointLearningComplete()
    df, prompts = task.simulate(_random_agent, args.num_simulations, max_chars=args.max_chars)

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