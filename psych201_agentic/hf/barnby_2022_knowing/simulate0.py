# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/barnby_2022_knowing``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp0).
INSTRUCTIONS = (
    "You are taking part in an online economic decision-making study. You have been "
    "matched with two anonymous partners, one for each phase of the study. The points "
    "you earn are pooled over a series of tasks and contribute to an overall total that "
    "enters a financial lottery.\n"
    "\n"
    "PHASE 1 - DECIDER. You are the decider. On each of 18 trials you see two options "
    "that each allocate points to you and your partner, and you choose the option you "
    "prefer. The options are shown as Option 1 and Option 2. Press A to select "
    "Option 1, or press B to select Option 2."
)

PHASE2_INTRO = (
    "PHASE 2 - RECIPIENT. You have been matched with a new partner. On each of 36 "
    "trials you see two options and predict which option your partner chose. You are "
    "then told whether your prediction was correct. Press A for Option 1, or press B "
    "for Option 2."
)

OPEN = "[HUMAN_RESPONSE]"
CLOSE = "[/HUMAN_RESPONSE]"

# The three source strings the participant can pick for the final forced choice,
# mapped to the narration label exactly as in build_jsonl.py.
FINAL_GUESS_OPTIONS = [
    "Trying to earn as much money as possible",
    "Trying to share as much money between us as possibe",
    "Trying to stop me from earning points",
]
FINAL_GUESS_LABEL = {
    "Trying to earn as much money as possible": "try to earn as much money as possible",
    "Trying to share as much money between us as possibe": "try to share the money equally",
    "Trying to stop me from earning points": "stop me from earning points",
}

FINAL_GUESS_SOURCE = {v: k for k, v in FINAL_GUESS_LABEL.items()}

CONDITIONS = ["Prosocial", "Individualist", "Competative"]

# The 18 Phase-1 (decider) option pairs as (self1, other1, self2, other2),
# from Table B.1 of the paper / the repo's exp0.csv.
DECIDER_ITEMS = [
    (8, 8, 10, 5), (12, 5, 8, 8), (10, 6, 8, 2), (12, 6, 10, 2),
    (9, 5, 9, 9), (12, 5, 9, 9), (8, 8, 8, 2), (6, 6, 6, 2),
    (6, 6, 10, 5), (7, 2, 8, 5), (10, 5, 10, 10), (7, 7, 7, 2),
    (8, 5, 8, 8), (8, 2, 9, 5), (12, 5, 10, 10), (11, 6, 9, 2),
    (6, 2, 8, 5), (7, 7, 10, 5),
]

# The 36 Phase-2 (recipient) option pairs, from the repo's exp0.csv.
RECIPIENT_ITEMS = [
    (7, 7, 7, 2), (8, 8, 12, 5), (7, 7, 10, 5), (6, 2, 6, 6),
    (8, 6, 7, 2), (10, 5, 10, 10), (8, 2, 8, 8), (11, 6, 9, 2),
    (12, 5, 9, 9), (8, 5, 8, 8), (9, 9, 9, 5), (6, 2, 8, 6),
    (9, 9, 12, 5), (10, 2, 12, 6), (10, 5, 8, 8), (10, 5, 6, 6),
    (10, 5, 7, 7), (12, 5, 8, 8), (12, 5, 10, 10), (7, 2, 7, 7),
    (8, 8, 10, 5), (10, 10, 10, 5), (8, 6, 6, 2), (8, 8, 8, 5),
    (8, 8, 8, 2), (9, 6, 8, 2), (8, 2, 10, 6), (9, 5, 9, 9),
    (6, 6, 10, 5), (10, 6, 8, 2), (8, 2, 9, 6), (12, 6, 10, 2),
    (7, 2, 8, 6), (6, 6, 6, 2), (10, 10, 12, 5), (9, 2, 11, 6),
]

# The partner's fixed answer (1 = Option 1, 2 = Option 2) for every Phase-2 option pair,
# per partner type, from the source repository's Task Specifications
# (ProsocialPartner.csv / IndividualistPartner.csv / CompetitivePartner.csv, column
# ANSWER); identical to the `answer` column of the repo's exp0.csv on all 36 items.
PARTNER_ANSWERS = {
    "Prosocial": {
        (6, 2, 6, 6): 2, (6, 2, 8, 6): 2, (6, 6, 6, 2): 1, (6, 6, 10, 5): 1,
        (7, 2, 7, 7): 2, (7, 2, 8, 6): 2, (7, 7, 7, 2): 1, (7, 7, 10, 5): 1,
        (8, 2, 8, 8): 2, (8, 2, 9, 6): 2, (8, 2, 10, 6): 2, (8, 5, 8, 8): 2,
        (8, 6, 6, 2): 1, (8, 6, 7, 2): 1, (8, 8, 8, 2): 1, (8, 8, 8, 5): 1,
        (8, 8, 10, 5): 1, (8, 8, 12, 5): 1, (9, 2, 11, 6): 2, (9, 5, 9, 9): 2,
        (9, 6, 8, 2): 1, (9, 9, 9, 5): 1, (9, 9, 12, 5): 1, (10, 2, 12, 6): 2,
        (10, 5, 6, 6): 2, (10, 5, 7, 7): 2, (10, 5, 8, 8): 2, (10, 5, 10, 10): 2,
        (10, 6, 8, 2): 1, (10, 10, 10, 5): 1, (10, 10, 12, 5): 1, (11, 6, 9, 2): 1,
        (12, 5, 8, 8): 2, (12, 5, 9, 9): 2, (12, 5, 10, 10): 2, (12, 6, 10, 2): 1,
    },
    "Individualist": {
        (6, 2, 6, 6): 1, (6, 2, 8, 6): 2, (6, 6, 6, 2): 1, (6, 6, 10, 5): 2,
        (7, 2, 7, 7): 2, (7, 2, 8, 6): 2, (7, 7, 7, 2): 2, (7, 7, 10, 5): 2,
        (8, 2, 8, 8): 1, (8, 2, 9, 6): 2, (8, 2, 10, 6): 2, (8, 5, 8, 8): 2,
        (8, 6, 6, 2): 1, (8, 6, 7, 2): 1, (8, 8, 8, 2): 1, (8, 8, 8, 5): 1,
        (8, 8, 10, 5): 2, (8, 8, 12, 5): 2, (9, 2, 11, 6): 2, (9, 5, 9, 9): 1,
        (9, 6, 8, 2): 1, (9, 9, 9, 5): 2, (9, 9, 12, 5): 2, (10, 2, 12, 6): 2,
        (10, 5, 6, 6): 1, (10, 5, 7, 7): 1, (10, 5, 8, 8): 1, (10, 5, 10, 10): 2,
        (10, 6, 8, 2): 1, (10, 10, 10, 5): 1, (10, 10, 12, 5): 2, (11, 6, 9, 2): 1,
        (12, 5, 8, 8): 1, (12, 5, 9, 9): 1, (12, 5, 10, 10): 1, (12, 6, 10, 2): 1,
    },
    "Competative": {
        (6, 2, 6, 6): 1, (6, 2, 8, 6): 1, (6, 6, 6, 2): 2, (6, 6, 10, 5): 2,
        (7, 2, 7, 7): 1, (7, 2, 8, 6): 1, (7, 7, 7, 2): 2, (7, 7, 10, 5): 2,
        (8, 2, 8, 8): 1, (8, 2, 9, 6): 1, (8, 2, 10, 6): 1, (8, 5, 8, 8): 1,
        (8, 6, 6, 2): 2, (8, 6, 7, 2): 2, (8, 8, 8, 2): 2, (8, 8, 8, 5): 2,
        (8, 8, 10, 5): 2, (8, 8, 12, 5): 2, (9, 2, 11, 6): 1, (9, 5, 9, 9): 1,
        (9, 6, 8, 2): 2, (9, 9, 9, 5): 2, (9, 9, 12, 5): 2, (10, 2, 12, 6): 1,
        (10, 5, 6, 6): 1, (10, 5, 7, 7): 1, (10, 5, 8, 8): 1, (10, 5, 10, 10): 1,
        (10, 6, 8, 2): 2, (10, 10, 10, 5): 2, (10, 10, 12, 5): 2, (11, 6, 9, 2): 2,
        (12, 5, 8, 8): 1, (12, 5, 9, 9): 1, (12, 5, 10, 10): 1, (12, 6, 10, 2): 2,
    },
}

# Participant-constant metadata columns read by build_jsonl.py's metadata(); a text
# simulator cannot produce real demographics/questionnaires, so these are NaN.
META_NAN_COLS = ["age", "gender", "education", "ethnicity", "religion",
                 "persec", "socref", "iq", "icar_rt"]

COLUMNS = [
    "participant_id", "trial", "phase", "condition", "game", "trial_source",
    "response", "option1_ppt", "option1_partner", "option2_ppt", "option2_partner",
    "diff1", "diff2", "answer", "correct", "incorrect", "cumulative_cor",
    "hi", "si", "final_guess",
] + META_NAN_COLS


def _options(s1, o1, s2, o2):
    return (
        f"Option 1 (You: {s1}, Partner: {o1}); "
        f"Option 2 (You: {s2}, Partner: {o2})"
    )


def _token(resp):
    return "A" if int(resp) == 1 else "B"


def _partner_answer(condition, s1, o1, s2, o2):
    """The partner's fixed, noise-free choice for this option pair (paper 2.2), looked
    up from the source's Task Specifications (PARTNER_ANSWERS)."""
    return PARTNER_ANSWERS[condition][(s1, o1, s2, o2)]


class SVOTask:
    """Modified social-value-orientation task, Barnby, Raihani & Dayan (2022),
    "Knowing me, knowing you", Cognition, 225, 105098.

    Design (2.2 The modified SVO task, pp. 6-7): Phase 1 (decider) is 18 SVO
    choices between two point allocations (Table B.1); Phase 2 (recipient) is 36
    predictions of a partner's choice with correct/incorrect feedback, followed by
    harmful-intent (HI) and self-interest (SI) 0-100 slider ratings and a 3-option
    forced choice about the partner's motive. Each participant is randomly matched
    with a prosocial, individualist, or competitive partner; the partner's choices
    are fixed a priori and noise-free, taken per option pair from the source
    repository's Task Specifications (PARTNER_ANSWERS), which match the `answer`
    column of the repo's exp0.csv on every item.

    ASSUMPTION: item order is randomized per participant (paper: "presented in a
    random order"); the repo's exp0.csv shows ~18/36 distinct orderings across the
    697 participants, consistent with per-participant shuffling.
    NOTE: the paper's verbal rule for the individualist partner ("highest payoff for
    themselves, and the prosocial option otherwise") does not hold on 5 of the 36
    option pairs; the lookup table follows the task as run, not the verbal rule.
    ASSUMPTION: the A/B response tokens are fixed (A = Option 1, B = Option 2), as
    in build_jsonl.py; they are not randomized per participant.
    ASSUMPTION: columns a text simulator cannot produce are dropped (rt,
    demographics, questionnaire scores, context-dependent SVO type labels, and the
    running propab/proprel/percentage_cor statistics); the demographics/questionnaire
    metadata columns are kept as NaN so build_jsonl.py's metadata() runs.

    The DataFrame matches exp0.csv minus those dropped columns.
    """

    def __init__(self):
        self.name = "barnby_2022_knowing_exp0"
        self.num_decider = 18
        self.num_recipient = 36

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            start = len(rows)
            condition = str(np.random.choice(CONDITIONS))
            decider_order = list(DECIDER_ITEMS)
            recipient_order = list(RECIPIENT_ITEMS)
            np.random.shuffle(decider_order)
            np.random.shuffle(recipient_order)

            prompt = INSTRUCTIONS
            trial = 0

            # Phase 1 - decider (block boundary before the phase).
            if max_chars is None or len(prompt) < max_chars:
                prompt += "\n\n"
                first = True
                for s1, o1, s2, o2 in decider_order:
                    if not first:
                        prompt += "\n"
                    first = False
                    prompt += f"Trial {trial + 1}. {_options(s1, o1, s2, o2)}. You press {OPEN}"
                    letter = agent(prompt, choice_options=["A", "B"])
                    response = 1 if letter == "A" else 2
                    prompt += f"{letter}{CLOSE}."
                    rows.append({
                        "participant_id": participant, "trial": trial, "phase": "decider",
                        "condition": condition, "game": "Choose", "trial_source": trial + 1,
                        "response": response, "option1_ppt": s1, "option1_partner": o1,
                        "option2_ppt": s2, "option2_partner": o2, "diff1": s1 - o1,
                        "diff2": s2 - o2, "answer": np.nan, "correct": np.nan,
                        "incorrect": np.nan, "cumulative_cor": np.nan, "hi": np.nan,
                        "si": np.nan, "final_guess": np.nan,
                        **{c: np.nan for c in META_NAN_COLS},
                    })
                    trial += 1

            # Phase 2 - recipient (block boundary before the phase).
            if max_chars is None or len(prompt) < max_chars:
                prompt += "\n\n" + PHASE2_INTRO + "\n"
                cum_cor = 0
                first = True
                for s1, o1, s2, o2 in recipient_order:
                    if not first:
                        prompt += "\n"
                    first = False
                    answer = _partner_answer(condition, s1, o1, s2, o2)
                    prompt += f"Trial {trial + 1}. {_options(s1, o1, s2, o2)}. " \
                              f"You predict the partner chose {OPEN}"
                    letter = agent(prompt, choice_options=["A", "B"])
                    response = 1 if letter == "A" else 2
                    correct = 1 if response == answer else 0
                    cum_cor += correct
                    feedback = "Correct." if correct == 1 else "Incorrect."
                    prompt += f"{letter}{CLOSE}. {feedback}"
                    rows.append({
                        "participant_id": participant, "trial": trial, "phase": "recipient",
                        "condition": condition, "game": "Guess", "trial_source": trial - 17,
                        "response": response, "option1_ppt": s1, "option1_partner": o1,
                        "option2_ppt": s2, "option2_partner": o2, "diff1": s1 - o1,
                        "diff2": s2 - o2, "answer": float(answer), "correct": float(correct),
                        "incorrect": float(1 - correct), "cumulative_cor": float(cum_cor),
                        "hi": np.nan, "si": np.nan, "final_guess": np.nan,
                        **{c: np.nan for c in META_NAN_COLS},
                    })
                    trial += 1

            # Post-phase-2 ratings (block boundary before the ratings).
            if max_chars is None or len(prompt) < max_chars:
                prompt += "\n\n"
                prompt += f"You rate how much you thought your partner was motivated by " \
                          f"harmful intent: {OPEN}"
                hi = int(agent(prompt, choice_options=[str(i) for i in range(101)]))
                prompt += f"{hi}{CLOSE} out of 100.\n"
                prompt += f"You rate how much you thought your partner was motivated by " \
                          f"self-interest: {OPEN}"
                si = int(agent(prompt, choice_options=[str(i) for i in range(101)]))
                prompt += f"{si}{CLOSE} out of 100.\n"
                prompt += f"You believe your partner's main aim was to {OPEN}"
                label = agent(prompt, choice_options=list(FINAL_GUESS_LABEL.values()))
                prompt += f"{label}{CLOSE}."
                fg = FINAL_GUESS_SOURCE[label]
                # Fill the participant-constant ratings onto this participant's recipient rows.
                for r in rows[start:]:
                    if r["phase"] == "recipient":
                        r["hi"] = float(hi)
                        r["si"] = float(si)
                        r["final_guess"] = fg

            prompts.append(prompt)

        df = pd.DataFrame(rows, columns=COLUMNS)
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

    task = SVOTask()
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
