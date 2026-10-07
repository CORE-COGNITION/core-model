# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/decker_2016_from``, format-identical
to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp0).
INSTRUCTIONS = (
    "You are a space explorer collecting space treasure. On each trial you first "
    "choose one of two spaceships. Each spaceship usually travels to one planet "
    "but sometimes to the other. After your spaceship travels, you arrive at a "
    "planet. On that planet you choose one of two aliens. If you pick the right "
    "alien, you find space treasure; otherwise you find nothing. The aliens' "
    "chances of giving treasure change slowly over time, so keep trying different "
    "choices.\n"
    "Press A to choose the first spaceship or B to choose the second spaceship. "
    "On each planet, press A to choose the first alien or B to choose the second alien."
)


class TwoStepTask:
    """Two-step "spaceship" task of Decker, Otto, Daw & Hartley (2016), "From
    Creatures of Habit to Goal-Directed Learners", Psychological Science, 27(6),
    848-858. Design described in Method / "Reinforcement-learning task
    (spaceship task)", p. 850: one first-stage choice between two spaceships,
    each leading to one of two planets with p=.7 (common) and to the other with
    p=.3 (rare); then one second-stage choice between two aliens on the reached
    planet, rewarded with space treasure according to a slowly drifting
    probability. The full game is 200 trials in four blocks separated by breaks
    (pp. 850-851).

    ASSUMPTION: the drifting reward probability for each of the 4 aliens is
    implemented as a bounded Gaussian random walk with per-trial SD 0.025,
    clipped to [0.2, 0.8] (the bounds cited in the paper), matching
    the reward process of the parent Daw et al. (2011) task the paper adapts.
    Each alien's initial probability is drawn uniformly in [0.2, 0.8].

    ASSUMPTION: the shipped exp0.csv has 151--200 paper-trials per participant
    (fewer than the paper's 200 for some participants, largely children: trials
    without a first- or second-stage response are absent from the source, paper
    p. 851). The simulator follows the paper
    and always generates 200 trials.

    ASSUMPTION: participant-level demographics (age / age_group / gender) are
    not parts of the generative task, so they are synthesized for each simulated
    participant from the empirical distribution of the original 59 subjects
    (age_group 20/20/19 children/adolescents/adults, gender 34f/25m, age drawn
    uniformly within the group's band).

    The token mapping is FIXED: by build_jsonl.py's ``_letter``, response 0->A,
    1->B at both stages (stage 2: the first/second alien on the planet reached,
    which ``state`` records). Space ship 0 commonly travels to planet A,
    spaceship 1 commonly to planet B, matching the data's transition structure.

    The DataFrame matches exp0.csv column-for-column (including the duplicated
    trial-level fields on both stage rows), with no columns dropped.
    """

    def __init__(self):
        self.name = "decker_2016_from_exp0"
        self.num_trials = 200       # paper trials per participant (paper pp. 850-851)
        self.trans_prob_common = 0.7  # spaceship -> common planet probability
        self.p_min, self.p_max = 0.2, 0.8  # alien reward-probability bounds
        self.drift_sd = 0.025       # per-trial random-walk step of alien probs

    def _simulate_demographics(self):
        group = np.random.choice(
            ["children", "adolescents", "adults"], p=[20 / 59, 20 / 59, 19 / 59])
        if group == "children":
            age = int(np.random.randint(8, 13))
        elif group == "adolescents":
            age = int(np.random.randint(13, 18))
        else:
            age = int(np.random.randint(18, 26))
        gender = str(np.random.choice(["f", "m"], p=[34 / 59, 25 / 59]))
        return age, group, gender

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            age, age_group, gender = self._simulate_demographics()
            alien_p = np.random.uniform(self.p_min, self.p_max, size=4)
            prompt = INSTRUCTIONS + "\n"
            for block in range(self.num_trials):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                # stage 1: spaceship choice (response 0 -> A, 1 -> B)
                prompt += "You choose a spaceship. You press [HUMAN_RESPONSE]"
                letter1 = agent(prompt, choice_options=["A", "B"])
                response1 = 0 if letter1 == "A" else 1
                prompt += f"{letter1}[/HUMAN_RESPONSE]."
                # probabilistic transition to a planet (70% common)
                common = bool(np.random.rand() < self.trans_prob_common)
                planet = 0 if bool((response1 == 0) == common) else 1
                prompt += f" You travel to planet {'A' if planet == 0 else 'B'}."
                # stage 2: alien choice (response 0/1 = first/second alien on the
                # planet reached; aliens 0/1 live on planet A, 2/3 on planet B)
                prompt += " You choose an alien. You press [HUMAN_RESPONSE]"
                letter2 = agent(prompt, choice_options=["A", "B"])
                response2 = 0 if letter2 == "A" else 1
                alien = 2 * planet + response2
                reward = int(np.random.rand() < alien_p[alien])
                prompt += (
                    f"{letter2}[/HUMAN_RESPONSE]. "
                    + ("You find space treasure!" if reward else "You find nothing.")
                    + "\n"
                )
                # drift every alien's reward probability one random-walk step
                alien_p = np.clip(
                    alien_p + np.random.normal(0.0, self.drift_sd, size=4),
                    self.p_min, self.p_max)
                trans = "common" if common else "rare"
                stage2_stims = "A" if planet == 0 else "B"
                rows.append({
                    "participant_id": participant, "trial": 2 * block, "block": block,
                    "stage": "stage1", "response": response1, "state": 0,
                    "reward": np.nan, "valid": 1, "trial_source": block,
                    "trans": trans, "stage2_stims": stage2_stims,
                    "stage1_resp": response1 + 1, "stage2_resp": alien + 3,
                    "reward_source": int(reward), "age": age,
                    "age_group": age_group, "gender": gender,
                })
                rows.append({
                    "participant_id": participant, "trial": 2 * block + 1, "block": block,
                    "stage": "stage2", "response": response2, "state": planet,
                    "reward": reward, "valid": 1, "trial_source": block,
                    "trans": trans, "stage2_stims": stage2_stims,
                    "stage1_resp": response1 + 1, "stage2_resp": alien + 3,
                    "reward_source": int(reward), "age": age,
                    "age_group": age_group, "gender": gender,
                })
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "block", "stage", "response", "state",
            "reward", "valid", "trial_source", "trans", "stage2_stims",
            "stage1_resp", "stage2_resp", "reward_source", "age", "age_group",
            "gender",
        ])
        df["participant_id"] = df["participant_id"].astype("int64")
        df["trial"] = df["trial"].astype("int64")
        df["block"] = df["block"].astype("int64")
        df["response"] = df["response"].astype("int64")
        df["state"] = df["state"].astype("int64")
        df["valid"] = df["valid"].astype("int64")
        df["trial_source"] = df["trial_source"].astype("int64")
        df["stage1_resp"] = df["stage1_resp"].astype("int64")
        df["stage2_resp"] = df["stage2_resp"].astype("int64")
        df["reward_source"] = df["reward_source"].astype("int64")
        df["age"] = df["age"].astype("int64")
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

    task = TwoStepTask()
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