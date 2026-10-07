# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/breslav_2022_shuffle``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp0), with the letter slots kept.
INSTRUCTIONS = (
    "You are playing a card game for M&M's with a grown-up on the other side of "
    "the table. A cylinder on the table already holds your 10 M&M's. Two "
    "face-down decks sit in front of you: one deck of cards is backed with black "
    "and white stripes, the other is backed with black dots on a white "
    "background. On each of 50 turns you pick one whole deck and the grown-up "
    "turns over that deck's top card. Every card shows, on its top half, how "
    "many M&M's you win, and on its bottom half, how many M&M's you lose; the "
    "difference between the two is the net M&M's you keep. The grown-up adds or "
    "removes M&M's from your cylinder to match. Your goal is to finish with as "
    "many M&M's as possible. As a demonstration you are first shown three "
    "example cards from each deck, never scored: the stripe deck's examples give "
    "+1, +1 and 0 net M&M's; the dot deck's examples give +2, +2 and -2 net "
    "M&M's.\n"
    "On each turn press {dot_letter} for the dot-backed deck or {stripe_letter} "
    "for the stripe-backed deck."
)


class ChildrensGamblingTask:
    """Children's Gambling Task, single experiment of Breslav et al. (2022),
    "Shuffle the Decks: Children Are Sensitive to Incidental Nonrandom Structure
    in a Sequential-Choice Task", Psychological Science, 33(3), 402-414.

    Design (Experimental procedure / Decks of cards, p. 552): 50 sequential free
    choices between an advantageous (ADV) and a disadvantageous (DIS) deck. Each
    deck has a fixed card order identical for every participant; choosing a deck
    turns over its current top card and advances that deck by one (the other
    deck's top stays). ADV pays win=1 (net +1 or 0, 25 each, EV .5); DIS pays
    win=2 with net +2 x25, -2 x10, -3 x5, -4 x10 (EV -.5). A child starts with
    10 M&M's in a cylinder and the assistant adds/removes to match net outcomes.
    The paper's Fig. 1 shows the first three cards of each deck as examples:
    ADV +1,+1,0; DIS +2,+2,-2. The identity of the deck (stripes vs dots) was
    randomly assigned to ADV/DIS per child in the paper and is not recorded in
    the data; the transcripts use stripes = ADV (response 1), dots = DIS
    (response 0) as a fixed convention, and this simulator keeps that mapping.

    Deck stacks are taken from the shipped data (authoritative): ADV is the
    a04..a53 net sequence, DIS the d04..d50 net sequence (Cards 4-50; the paper
    shows the first 3 as examples, so the 50 play cards start at Card 4).

    ASSUMPTION: the shipped data only reveal 47 DIS cards (d04..d50, nets known);
    the last three DIS cards (d51..d53) are not represented in the data.
    Following the source's restart rule for the ADV deck (a51..a53 are cards 1-3
    again), the simulator restarts the DIS deck at cards 1-3 (+2, +2, -2) for
    d51..d53, which a uniform-random agent essentially never reaches in 50
    trials (it would need >=48 DIS choices).

    ASSUMPTION: one real row (card a53, a data typo) records win=1, lose=1 for a
    net of 0; the simulator always derives lose = net - win (a53 -> lose -1),
    treating net_outcome as authoritative.

    The DataFrame matches exp0.csv minus ``age`` (a participant demographic a text
    simulator cannot produce) and ``rt`` (absent from the schema).
    """

    def __init__(self):
        self.name = "breslav_2022_shuffle_exp0"
        self.num_trials = 50
        self.initial_mms = 10
        # ADV (stripe, response 1) deck, play cards a04..a53, one net outcome each.
        self.adv_ids = [f"a{i:02d}" for i in range(4, 54)]
        self.adv_nets = [
            1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0,
            1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0,
            0, 1, 1, 0,
        ]
        # DIS (dot, response 0) deck, cards d04..d53; nets known for d04..d50,
        # d51..d53 restart the deck at cards 1-3.
        self.dis_ids = [f"d{i:02d}" for i in range(4, 54)]
        self.dis_nets = [
            2, -4, 2, -2, 2, -3, -4, 2, -4, 2, -3, -2, 2, -4, -2, 2, 2, 2, -4, 2,
            -4, 2, -2, -3, -2, 2, 2, -4, -2, -3, 2, 2, 2, -2, -4, 2, 2, 2, 2, -2,
            2, -4, 2, -2, 2, -3, -4, 2, 2, -2,
        ]

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            # per-participant A/B -> deck mapping, exactly as in build_jsonl.py.
            dot_letter, stripe_letter = (
                ("A", "B") if participant % 2 == 0 else ("B", "A")
            )
            deck_letter = {0: dot_letter, 1: stripe_letter}
            deck_name = {0: "dot", 1: "stripe"}
            prompt = INSTRUCTIONS.format(dot_letter=dot_letter,
                                         stripe_letter=stripe_letter)
            cup = self.initial_mms
            adv_idx, dis_idx = 0, 0
            prev_response = None
            last_chosen, last_win, last_choose_adv = None, None, None
            completed = True
            for trial in range(self.num_trials):
                if max_chars is not None and len(prompt) >= max_chars:
                    completed = False
                    break
                adv_card = self.adv_ids[adv_idx]
                dis_card = self.dis_ids[min(dis_idx, len(self.dis_ids) - 1)]
                prompt += "\nYou press [HUMAN_RESPONSE]"
                letter = agent(prompt, choice_options=[dot_letter, stripe_letter])
                response = 0 if letter == dot_letter else 1
                if response == 0:
                    card, net = dis_card, self.dis_nets[min(dis_idx, len(self.dis_nets) - 1)]
                    dis_idx += 1
                else:
                    card, net = adv_card, self.adv_nets[adv_idx]
                    adv_idx += 1
                win = 2 if response == 0 else 1
                lose = net - win
                cup += net
                prompt += (
                    f"{letter}[/HUMAN_RESPONSE] and pick the "
                    f"{deck_name[response]}-backed deck. Its top card shows "
                    f"{win} M&M's won and {abs(lose)} M&M's lost, a net of "
                    f"{net:+d} M&M's. Your cylinder now holds {cup} M&M's."
                )
                switch = None if prev_response is None else float(response != prev_response)
                rows.append({
                    "participant_id": participant, "trial": trial,
                    "response": response, "reward": net,
                    "adv_top_card": adv_card, "dis_top_card": dis_card,
                    "chosen_card_id": card, "choose_adv": response,
                    "win": win, "lose": lose, "net_outcome": net,
                    "switch": switch,
                    "last_chosen_card": last_chosen,
                    "last_trial_win": last_win,
                    "last_trial_choose_adv": last_choose_adv,
                })
                prev_response = response
                last_chosen = card
                last_win = 1.0 if net > 0 else -1.0
                last_choose_adv = 1.0 if response == 1 else -1.0
            if completed:
                prompt += f"\nThe 50 choices are over. You end with {cup} M&M's."
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "reward", "adv_top_card",
            "dis_top_card", "chosen_card_id", "choose_adv", "win", "lose",
            "net_outcome", "switch", "last_chosen_card", "last_trial_win",
            "last_trial_choose_adv",
        ])
        df["switch"] = df["switch"].astype("float")
        df["last_chosen_card"] = df["last_chosen_card"].astype("object")
        df["last_trial_win"] = df["last_trial_win"].astype("float")
        df["last_trial_choose_adv"] = df["last_trial_choose_adv"].astype("float")
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

    task = ChildrensGamblingTask()
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