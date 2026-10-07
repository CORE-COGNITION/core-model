# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/cohen_2020_rational``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp0). The mine-choice and
# attribution tokens (A/B, Y/N) are fixed, not randomized per participant.
INSTRUCTIONS = (
    "You are a gold miner in the Wild West. Each time you find gold you earn a small "
    "real bonus; each time you find rocks you lose a small amount. On every trial you "
    "see two mines, one on the left and one on the right, and you choose one in which "
    "to dig. Within each block one mine gives gold most of the time and the other rarely "
    "does; the mines stay on the same side for the whole block, so try to figure out "
    "which mine is better and keep choosing it. Press A to choose the left mine or B to "
    "choose the right mine. After you choose, you see either gold or rocks appear in "
    "front of the mine you selected. You play in three different territories, each with "
    "its own hidden agent that sometimes intervenes. In millionaire territory a nice "
    "millionaire sometimes puts gold in both mines. In robber territory a mean robber "
    "sometimes replaces the gold with rocks. In sheriff territory a sneaky sheriff "
    "sometimes randomly puts rocks and gold in either mine. The hidden agents intervene "
    "only on a small number of trials. After every outcome you indicate whether you "
    "think the hidden agent caused that outcome by pressing Y for yes or N for no."
)


class GoldMiningExploration:
    """Two-armed mining RL with latent-agent attribution, from Cohen, Nussenbaum,
    Dorfman, Gershman & Hartley (2020), "The rational use of causal inference to
    guide reinforcement learning strengthens with age", npj Science of Learning,
    5(1), 16.

    Design (Methods/"Reinforcement learning task", p. 6): 3 blocks of 50 trials,
    one block per hidden-agent territory. Within a block one mine yields gold
    with probability 0.8 and the other with 0.2; the mines stay on the same side
    for the whole block. A hidden agent intervenes on 30% of trials per
    territory: the millionaire puts gold in both mines (feedback = gold regardless
    of the choice), the robber replaces the gold with rocks (feedback = rocks
    always), and the sheriff randomly puts rocks and gold in either mine
    (feedback = a fair coin). Participants choose a mine, observe the realized
    outcome, then report whether they think the hidden agent caused it.

    Simulated generative process per participant: sample a territory order
    (random permutation of millionaire/robber/sheriff) and a random side for the
    good (0.8) mine in each block; on each trial draw an intervention indicator
    (Bernoulli 0.3) and draw the realized feedback from the base probability of
    the chosen mine on non-intervention trials, or from the territory's forced
    outcome on intervention trials. These reproduce the empirical gold rates in
    exp0.csv (P(gold | chosen good/bad mine) = 0.85/0.43 in millionaire,
    0.55/0.11 in robber, 0.70/0.28 in sheriff).

    ASSUMPTION (response coding): the shipped data record ``response`` with the
    source key 1 = left = button A, 0 = right = button B (see the repo's
    "Text-format conversion" note and build_jsonl.py, which map response == 1 to
    "A"), so the simulator records response = 1 when the agent presses A.
    ``optimal_choice`` follows the source key (hartleylabnyu/dev-causal-inference
    README: "whether the subject chose the better mine, 0 = no, 1 = yes"), i.e.
    1 when the chosen mine is the block's good (0.8) mine.
    ASSUMPTION (demographics): ``participant_id`` is generated 1..N; ``age`` /
    ``age_group`` / ``gender`` / ``valid`` are drawn from the shipped data's
    distributions (age_group uniform over kid/teen/adult, age uniform within the
    group's range, gender m/f, valid with probability 90/101; the ~11 invalid
    participants carry NaN age and gender "na"). ``version`` is drawn uniformly
    from the six task versions A-F (lowercase variants in the source are treated
    as their uppercase label). These fields never surface in the narrative.

    The DataFrame matches exp0.csv minus ``rt`` (a reaction time a text
    simulator cannot produce), with the same column names, dtypes and value
    conventions.
    """

    def __init__(self):
        self.name = "cohen_2020_rational_exp0"
        self.blocks = 3                  # one block per territory
        self.trials_per_block = 50
        self.good_prob = 0.8             # good mine yields gold with this probability
        self.bad_prob = 0.2
        self.intervention_prob = 0.3     # hidden agent acts on 30% of trials
        self.sheriff_coin = 0.5          # sheriff's intervention outcome is a fair coin
        self.territories = ["millionaire", "robber", "sheriff"]
        self.valid_prob = 90 / 101       # usability rate in the shipped data

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        rng = np.random.default_rng()
        for participant in tqdm(range(num_simulations)):
            pid = participant + 1  # 1-indexed participant_id

            # per-participant metadata (never narrated)
            valid = 1 if rng.random() < self.valid_prob else 0
            if valid:
                age_group = str(rng.choice(["kid", "teen", "adult"]))
                lo, hi = {"kid": (7.0, 13.0), "teen": (13.0, 18.0),
                          "adult": (18.0, 26.0)}[age_group]
                age = float(rng.uniform(lo, hi))
                gender = str(rng.choice(["m", "f"]))
            else:
                age_group, age, gender = np.nan, np.nan, "na"
            version = str(rng.choice(["A", "B", "C", "D", "E", "F"]))

            prompt = INSTRUCTIONS
            territory_order = rng.permutation(self.territories).tolist()
            for block in range(self.blocks):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                cond = territory_order[block]
                # 0=left is the good (0.8) mine this block, 1=right
                good_side = int(rng.integers(0, 2))
                p_left = self.good_prob if good_side == 0 else self.bad_prob
                p_right = self.good_prob if good_side == 1 else self.bad_prob
                prompt += f"\nA new block begins. You are in {cond} territory."
                for trial_in_block in range(self.trials_per_block):
                    trial = block * self.trials_per_block + trial_in_block

                    prompt += "\nYou press [HUMAN_RESPONSE]"
                    letter = agent(prompt, choice_options=["A", "B"])
                    response = 1 if letter == "A" else 0  # A = left = 1 (source key)
                    base_prob = p_left if response == 1 else p_right
                    intervene = rng.random() < self.intervention_prob
                    if intervene:
                        if cond == "robber":
                            feedback = 0
                        elif cond == "millionaire":
                            feedback = 1
                        else:  # sheriff
                            feedback = int(rng.random() < self.sheriff_coin)
                    else:
                        feedback = int(rng.random() < base_prob)
                    outcome = "gold" if feedback == 1 else "rocks"
                    prompt += f"{letter}[/HUMAN_RESPONSE]. You find {outcome}. Agent caused it? [HUMAN_RESPONSE]"
                    guess = agent(prompt, choice_options=["Y", "N"])
                    latent_guess = 1 if guess == "Y" else 0
                    prompt += f"{guess}[/HUMAN_RESPONSE]."
                    rows.append({
                        "participant_id": pid, "trial": trial, "block": block,
                        "trial_in_block": trial_in_block + 1, "condition": cond,
                        "version": version,
                        "mine_prob_win_left": p_left, "mine_prob_win_right": p_right,
                        "response": response, "feedback": feedback,
                        "latent_guess": latent_guess,
                        "optimal_choice": int(base_prob == self.good_prob),
                        "valid": valid, "age": age, "age_group": age_group,
                        "gender": gender,
                    })
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "block", "trial_in_block", "condition",
            "version", "mine_prob_win_left", "mine_prob_win_right", "response",
            "feedback", "latent_guess", "optimal_choice", "valid", "age",
            "age_group", "gender",
        ])
        # match shipped dtypes
        df["participant_id"] = df["participant_id"].astype("int64")
        df["trial"] = df["trial"].astype("int64")
        df["block"] = df["block"].astype("int64")
        df["trial_in_block"] = df["trial_in_block"].astype("int64")
        df["response"] = df["response"].astype("int64")
        df["feedback"] = df["feedback"].astype("int64")
        df["latent_guess"] = df["latent_guess"].astype("int64")
        df["optimal_choice"] = df["optimal_choice"].astype("int64")
        df["valid"] = df["valid"].astype("int64")
        df["mine_prob_win_left"] = df["mine_prob_win_left"].astype("float64")
        df["mine_prob_win_right"] = df["mine_prob_win_right"].astype("float64")
        df["age"] = df["age"].astype("float64")
        return df, prompts


def _random_agent(prompt, choice_options):
    """Uniform-random choice, matching the reference example's agent."""
    return str(np.random.choice(choice_options))


def main():
    parser = argparse.ArgumentParser(
        description="Smoke-test this simulator with a uniform-random agent.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3, help="number of simulated participants (default: 3)")
    parser.add_argument("--max-chars", type=int, default=None, help="stop each participant at a block boundary at/past this many chars")
    parser.add_argument("--seed", type=int, default=None, help="numpy random seed, for reproducible runs")
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    task = GoldMiningExploration()
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