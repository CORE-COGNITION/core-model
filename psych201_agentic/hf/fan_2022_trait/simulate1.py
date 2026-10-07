# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 of ``Hugging-Brain/fan_2022_trait`` (Study 2 bandit
+ reward-prediction task), format-identical to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp1); the two instruction blocks
# are joined with a single space on the first line.
INSTRUCTIONS = (
    "You are playing a two-slot-machine game to earn as many coins as you can. "
    "In each round, a fresh pair of slot machines appears on screen, one on the left and one on the right. "
    "On each play, you choose one machine; the machine pays out a number of coins, which may be positive or negative. "
    "Each round lasts 10 plays, and then a new pair of machines appears. "
    "Press A to play the left machine or B to play the right machine. "
    "After each round of the game, you are asked to make reward predictions for the two machines you just played. "
    "For each machine, first type your estimate of how many coins it will pay out on its next play (an integer, "
    "which may be negative), then rate how confident you are in that estimate from 0 to 10."
)

CONDITIONS = {
    1: (True, False),   # FS: left fluctuates, right stable
    2: (False, True),   # SF: left stable, right fluctuates
    3: (True, True),    # FF: both fluctuate
    4: (False, False),  # SS: both stable
}

# Free-response candidate sets (the agent picks one token per decision).
EST_OPTIONS = [str(i) for i in range(-50, 51)]
CONF_OPTIONS = [str(i) for i in range(0, 11)]


def _fmt(x):
    f = float(x)
    return str(int(f)) if f == int(f) else str(f)


class TwoSlotBanditPredict:
    """Restless two-slot-machine bandit plus reward-prediction task, Study 2 of
    Fan, Gershman & Phelps (2023), "Trait somatic anxiety is associated with
    reduced directed exploration and underestimation of uncertainty", Nature
    Human Behaviour, 7, 102-113.

    Design (Supplementary Methods, "Behavioral Task / Experiment 2", paper SI
    p.3-4): identical bandit to Study 1 (30 rounds x 10 A/B plays between a
    fresh stable/fluctuating pair) but, after each round, the participant
    predicts how many coins each machine will generate on its next play (free
    integer estimate, may be negative) and reports a 0-10 confidence in that
    estimate. Choice 1 = left machine (option 1, press A), 0 = right machine
    (option 2, press B), as in the source data (C = 1 pays reward1). Which
    machine is predicted first is randomized per round (paper Methods), and the
    prediction rows carry one running ``trial`` counter per participant under
    task_id 30, as in exp1.csv.

    ASSUMPTION: as in exp0, the generative constants (initial mean ~
    round(N(0, 10)), fluctuating-arm drift ~ round(N(0, 2)) per play, reward ~
    round(N(mu, 1)), condition 1=FS / 2=SF / 3=FF / 4=SS per round) were
    reverse-engineered from the shipped exp1.csv (the paper's Methods are
    paywalled and no task code is on OSF); re-verified on the data here.

    ASSUMPTION: the paper/SI do not specify a generative model for the
    prediction responses (they are human beliefs), so the simulator asks the
    agent for a free integer estimate (candidate set -50..50) and a 0-10
    confidence; prediction rows are generated for every round of every
    participant (the shipped data has ~8% of participants without prediction
    rows and a few rounds missing per participant - treated as dropout, not
    design).

    ASSUMPTION: the prediction-phase covariate ``type_pred`` (a per-round
    binary flag in the shipped data) and the belief/state columns ``true_m1``,
    ``true_m2``, ``curr_est_m``, ``curr_est_s``, ``curr_true_m`` are dropped
    because their exact generative semantics could not be pinned down from the
    data.

    The DataFrame matches exp1.csv minus ``rt``/``conf_rt``, the model-derived
    columns (V, RU, VTU, TU, *_old, est_m1/2, est_s1/2, C_pred, C_pred_prob,
    curr_est_m/s, curr_true_m, true_m1/2, type_pred) and the
    questionnaire/demographic columns (age, gender, STAIT_*, STICSAT_*,
    Factor*).
    """

    def __init__(self):
        self.name = "fan_2022_trait_exp1"
        self.num_rounds = 30     # fresh pair of slot machines each round
        self.num_plays = 10      # free choices per round
        self.init_sd = 10.0      # mu ~ round(N(0, init_sd)) per arm per round
        self.drift_sd = 2.0      # fluctuating arm's mean drift ~ round(N(0, drift_sd))
        self.reward_sd = 1.0     # reward ~ round(N(mu, reward_sd))

    def _new_mean(self):
        return int(np.round(np.random.normal(0.0, self.init_sd)))

    def _step(self):
        return int(np.round(np.random.normal(0.0, self.drift_sd)))

    def _reward(self, mu):
        return int(np.round(np.random.normal(mu, self.reward_sd)))

    def _bandit_play(self, agent, prompt, rnd, trial, mu1, mu2, condition):
        """Narrate one free A/B play; returns (prompt, bandit_row)."""
        prompt += "\nYou press [HUMAN_RESPONSE]"
        letter = agent(prompt, choice_options=["A", "B"])
        response = 1 if letter == "A" else 0
        side = "left" if response == 1 else "right"
        reward1 = self._reward(mu1)
        reward2 = self._reward(mu2)
        reward = reward1 if response == 1 else reward2
        if reward >= 0:
            prompt += (f"{letter}[/HUMAN_RESPONSE] for the {side} machine. "
                       f"You gain {_fmt(reward)} coins.")
        else:
            prompt += (f"{letter}[/HUMAN_RESPONSE] for the {side} machine. "
                       f"You lose {_fmt(-reward)} coins.")
        chosen = mu1 if response == 1 else mu2
        other = mu2 if response == 1 else mu1
        row = {
            "participant_id": None, "task_id": rnd, "trial": trial,
            "response": response, "reward": reward, "correct": int(chosen > other),
            "condition": condition, "mu1": mu1, "mu2": mu2,
            "reward1": reward1, "reward2": reward2,
            "block": np.nan, "pred_machine": np.nan,
            "pred_num": np.nan, "conf_rating": np.nan,
        }
        return prompt, row

    def _prediction(self, agent, prompt, rnd, mu1, mu2, trial0=0):
        """Narrate the reward-prediction block for one round; returns
        (prompt, pred_rows)."""
        prompt += f"\nNow you make reward predictions for round {rnd + 1}'s two machines."
        rows = []
        trial = trial0
        machines = [(0, mu1), (1, mu2)]
        if np.random.rand() < 0.5:   # left-or-right-first is randomized per round
            machines.reverse()
        for machine, mu in machines:
            side = "left" if machine == 0 else "right"
            prompt += ("\nFor the left machine, your prediction of next-play coins: "
                       if machine == 0 else
                       "\nFor the right machine, your prediction of next-play coins: ")
            prompt += "[HUMAN_RESPONSE]"
            est_token = agent(prompt, choice_options=EST_OPTIONS)
            prompt += f"{est_token}[/HUMAN_RESPONSE]."
            est = int(est_token)
            rows.append({
                "participant_id": None, "task_id": 30, "trial": trial,
                "response": est, "reward": np.nan, "correct": np.nan,
                "condition": np.nan, "mu1": np.nan, "mu2": np.nan,
                "reward1": np.nan, "reward2": np.nan, "block": rnd,
                "pred_machine": machine, "pred_num": est, "conf_rating": np.nan,
            })
            trial += 1
            prompt += "\nYour confidence in that estimate (0-10): [HUMAN_RESPONSE]"
            conf_token = agent(prompt, choice_options=CONF_OPTIONS)
            prompt += f"{conf_token}[/HUMAN_RESPONSE]."
            conf = int(conf_token)
            rows.append({
                "participant_id": None, "task_id": 30, "trial": trial,
                "response": conf, "reward": np.nan, "correct": np.nan,
                "condition": np.nan, "mu1": np.nan, "mu2": np.nan,
                "reward1": np.nan, "reward2": np.nan, "block": rnd,
                "pred_machine": machine, "pred_num": np.nan, "conf_rating": conf,
            })
            trial += 1
        return prompt, rows

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            prompt = INSTRUCTIONS
            pred_trial = 0
            for rnd in range(self.num_rounds):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                condition = int(np.random.randint(1, 5))
                fluc1, fluc2 = CONDITIONS[condition]
                mu1, mu2 = self._new_mean(), self._new_mean()
                prompt += f"\nRound {rnd + 1}: A new pair of slot machines appears."
                for trial in range(self.num_plays):
                    prompt, brow = self._bandit_play(
                        agent, prompt, rnd, trial, mu1, mu2, condition)
                    brow["participant_id"] = f"P{participant:03d}"
                    rows.append(brow)
                    if fluc1:
                        mu1 += self._step()
                    if fluc2:
                        mu2 += self._step()
                prompt, pred_rows = self._prediction(agent, prompt, rnd, mu1, mu2, pred_trial)
                pred_trial += len(pred_rows)
                for r in pred_rows:
                    r["participant_id"] = f"P{participant:03d}"
                rows.extend(pred_rows)
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "task_id", "trial", "response", "reward",
            "correct", "condition", "mu1", "mu2", "reward1", "reward2",
            "block", "pred_machine", "pred_num", "conf_rating",
        ])
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

    task = TwoSlotBanditPredict()
    df, prompts = task.simulate(_random_agent, args.num_simulations,
                                max_chars=args.max_chars)

    print(f"name: {task.name}")
    print(f"df shape: {df.shape}")
    print("dtypes:")
    print(df.dtypes.to_string())
    print("head:")
    print(df.head(12).to_string())
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
