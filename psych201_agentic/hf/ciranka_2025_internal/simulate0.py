# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/ciranka_2025_internal``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import math
import random

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim instruction block from build_jsonl.py (transcribe_exp0), the
# per-participant A/B slots kept.
INSTRUCTIONS = (
    "You are playing a lottery game. On each round you choose between two "
    "jars from which a random marble is drawn: a safe jar containing only "
    "blue marbles that always pays 5 points, and a risky jar containing "
    "both blue and red marbles that pays more (8, 20, or 50 points) but "
    "only if the marble you draw is blue. In this session you press "
    "{safe_letter} to choose the SAFE jar and {risky_letter} to "
    "choose the RISKY jar. "
    "On some rounds the risky jar's winning chance is stated directly as "
    "a proportion of blue marbles in the jar; on other rounds you instead "
    "watch a brief sample of 9 marbles drawn from the jar and judge its "
    "chance from that sample, then rate how sure you are with a second "
    "slider. On every round you first set a slider (0-100) to estimate "
    "the percent chance of drawing a blue marble, then make your choice. "
    "In the second half of the game you also see how another participant "
    "chose in the same lottery before you choose. Points accumulate and "
    "are converted to a bonus at the end.\n"
)

# Verbatim 9-marble display patterns observed in exp0.csv: probGamble -> (red, blue).
MARBLE_PATTERNS = {
    0.125: ("1,4,1,2,0", "0,0,0,0,1"),   # 8 red, 1 blue
    0.25: ("1,1,3,1,1", "0,0,1,0,1"),    # 7 red, 2 blue
    0.375: ("1,3,0,2,0", "0,1,1,0,1"),   # 6 red, 3 blue
    0.5: ("0,0,2,2,0", "1,1,2,0,1"),     # 4 red, 5 blue
    0.675: ("0,0,1,1,1", "1,1,1,3,0"),   # 3 red, 6 blue
    0.75: ("0,1,1,0,0", "1,3,1,1,1"),    # 2 red, 7 blue
}

DESCRIPTION_PERCENT = dict(
    PercentBlueShownAbs=2.2, PercentRedShownAbs=2.2,
    PercentBlueShownRel=0.5, PercentRedShownRel=0.5, TotalNShown=198,
)


def _letters(pid):
    """A/B option tokens, exactly as build_jsonl.py assigns them."""
    rng = random.Random(int(pid))
    order = rng.sample(["safe", "risky"], 2)
    return {order[0]: "A", order[1]: "B"}


class DevelopingMarbles:
    """The marble lottery of Ciranka & van den Bos (2025), "Internal
    uncertainty impacts social information use in risky choice across
    adolescence", Communications Psychology 3:137; Methods "Task and
    procedure", "Experimental manipulation of external uncertainty",
    "Experimental manipulation of social information" (p. 2).

    Design recovered from the paper and exp0.csv: 144 gambles per
    participant, split into a solochoice phase (blocks 0-71) and a
    socialchoice phase (blocks 72-143). Within each phase the same 18
    value x probability combinations (valueGamble 8/20/50, probGamble
    0.125/0.25/0.375/0.5/0.675/0.75) appear twice as from_description and
    twice as from_experience, in randomised order. A from_description
    gamble is narrated from its stated blue proportion, a from_experience
    gamble from a predetermined 9-marble sample. Each gamble yields an
    estimate slider row plus (from_experience only) a confidence slider
    row, then a risky/safe choice row.

    ASSUMPTION: the response-token mapping reproduces build_jsonl.py's
    per-participant A/B assignment (``random.Random(int(pid))``) so the
    generated prompt and the round-tripped transcript are byte-identical.
    ASSUMPTION: probGamble 0.675 is used (as in the data) where the paper
    lists 0.625; the 9-marble blue counts follow the data's predetermined
    representative samples (blue = floor(p*9 + 0.5): 1/2/3/5/6/7 for
    p=0.125..0.75), shown verbatim in ``MARBLE_PATTERNS``.
    ASSUMPTION: the session's `startTime` date, `age`, `gender`,
    `age_group`, `rt`, and the jsPsych `key_press`/`riskyKey` codes are
    not producible from narrative text and are dropped.
    ASSUMPTION: social-information choices (OtherChoseRisk) came from a
    previous study's participants and are not in this dataset; they are
    synthesised per the paper's matching rule (peer ~20% more risky than
    the participant's own solo rate, capped at 0.9): peer risk rate =
    min(0.9, solo risky rate + 0.20), one Bernoulli draw per social trial.
    """

    def __init__(self):
        self.name = "ciranka_2025_internal_exp0"
        self.num_gambles = 144          # 72 solo + 72 social
        self.gambles_per_phase = 72
        self.values = [8, 20, 50]
        self.probs = [0.125, 0.25, 0.375, 0.5, 0.675, 0.75]
        self.conditions = ["from_description", "from_experience"]
        self.value_sure = 5

    def _schedule(self, rng):
        """144 trials as (phase, condition, value, prob) tuples, shuffled
        within each phase block; the phase order is fixed (solo first)."""
        trials = []
        for phase in ("solochoice", "socialchoice"):
            block = []
            for value in self.values:
                for prob in self.probs:
                    for cond in self.conditions:
                        block.append((value, prob, cond))
                        block.append((value, prob, cond))
            rng.shuffle(block)
            trials.extend((phase,) + t for t in block)
        return trials

    @staticmethod
    def _gamble_line(cond, value, prob):
        if cond == "from_description":
            n = int(round(prob * 100))
            return (f"The risky jar, which offers {value} points if you draw "
                    f"blue, is shown with 100 marbles, "
                    f"{n} of them blue, so it wins with probability {n}%. "
                    f"Choosing it risks drawing red for nothing. The safe "
                    f"jar always draws blue and pays 5 points.")
        blue = min(9, max(0, int(prob * 9 + 0.5)))
        red = 9 - blue
        return (f"You see a sample of {red} red and {blue} blue marbles "
                f"drawn from the risky jar, which offers {value} points if "
                f"you draw blue; the safe jar always draws blue and pays 5 "
                f"points.")

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            rng = np.random.default_rng(participant)
            letters = _letters(participant)
            schedule = self._schedule(random.Random(participant))
            prompt = INSTRUCTIONS.format(
                safe_letter=letters["safe"], risky_letter=letters["risky"])

            cumulated = 0
            solo_risky = []
            trial = 0

            block_idx = 0
            for (phase, value, prob, cond) in schedule:
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                index = block_idx
                peer = None
                if phase == "socialchoice":
                    # peer synthesis: one per participant, sticky across phase
                    if index == self.gambles_per_phase:
                        solo_rate = (np.mean(solo_risky) if solo_risky else 0.5)
                        peer_p = min(0.9, solo_rate + 0.20)
                    peer = 1 if rng.random() < peer_p else 0

                line = self._gamble_line(cond, value, prob)
                if peer is not None:
                    line += (" A peer previously chose the risky option."
                             if peer == 1
                             else " A peer previously chose the safe option.")
                prompt += line + "\n"

                # estimate slider (free response, 0-100)
                prompt += ("You estimate the chance of drawing a blue marble "
                           "as [HUMAN_RESPONSE]")
                est = agent(prompt, choice_options=list(range(101)))
                est = int(est)
                prompt += f"{est}[/HUMAN_RESPONSE]%.\n"

                # confidence slider, only from_experience
                conf = None
                if cond == "from_experience":
                    prompt += ("You rate how sure you are about that estimate "
                               "as [HUMAN_RESPONSE]")
                    conf = int(agent(prompt, choice_options=list(range(101))))
                    prompt += f"{conf}[/HUMAN_RESPONSE].\n"

                # choice, free response on the A/B token set
                prompt += "You choose [HUMAN_RESPONSE]"
                letter = agent(prompt, choice_options=[letters["safe"],
                                                       letters["risky"]])
                letter = str(letter)
                if letter == letters["risky"]:
                    choice_label, response = "risky", 1
                else:
                    choice_label, response = "safe", 0
                if response == 1:
                    reward = value if rng.random() < prob else 0
                else:
                    reward = self.value_sure
                if phase == "solochoice":
                    solo_risky.append(response)
                prompt += (f"{letter}[/HUMAN_RESPONSE] (the {choice_label} jar). "
                           f"You win {reward} points.\n")
                cumulated += reward

                # --- row bookkeeping ---
                common = {
                    "participant_id": participant, "block": index,
                    "condition": cond, "valid": 1, "valueGamble": value,
                    "probGamble": prob, "Social1Ind0": 1 if phase == "socialchoice" else 0,
                    "payoff": reward, "cumulatedPayoff": cumulated,
                    "valueSure": self.value_sure, "phase": phase,
                    "OtherChoseRisk": peer if peer is not None else float("nan"),
                    "ChooseRisk": response,
                }
                if cond == "from_description":
                    red_str, blue_str = "99", "99"
                    common.update(DESCRIPTION_PERCENT)
                else:
                    blue = min(9, max(0, int(prob * 9 + 0.5)))
                    red_str, blue_str = MARBLE_PATTERNS[prob]
                    common.update({
                        "PercentBlueShownAbs": blue / 45,
                        "PercentRedShownAbs": (9 - blue) / 45,
                        "PercentBlueShownRel": blue / 9,
                        "PercentRedShownRel": (9 - blue) / 9,
                        "TotalNShown": 9,
                    })
                common["red_marbles"] = red_str
                common["blue_marbles"] = blue_str

                rows.append({**common, "trial": trial,
                             "response": est, "response_type": "estimate",
                             "reward": float("nan")})
                trial += 1
                if conf is not None:
                    rows.append({**common, "trial": trial,
                                 "response": conf, "response_type": "confidence",
                                 "reward": float("nan")})
                    trial += 1
                rows.append({**common, "trial": trial,
                             "response": response, "response_type": "choice",
                             "reward": float(reward)})
                trial += 1
                block_idx += 1

            prompts.append(prompt.strip())

        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "block", "response", "response_type",
            "reward", "condition", "valid", "red_marbles", "blue_marbles",
            "OtherChoseRisk", "ChooseRisk", "valueGamble", "probGamble",
            "Social1Ind0", "payoff", "cumulatedPayoff", "valueSure",
            "PercentBlueShownAbs", "PercentRedShownAbs", "PercentBlueShownRel",
            "PercentRedShownRel", "TotalNShown", "phase",
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

    task = DevelopingMarbles()
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