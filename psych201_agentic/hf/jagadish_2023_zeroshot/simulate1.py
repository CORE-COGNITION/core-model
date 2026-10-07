# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 of ``Hugging-Brain/jagadish_2023_zeroshot``
(change-point composition rule), format-identical to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import json

import numpy as np
import pandas as pd
from tqdm import tqdm

ARMS = ["S", "D", "F", "J", "K", "L"]
COMPOSITION_RULE = "switches partway along the row from one company's pattern to the other's"


def _intro(phase):
    if phase == "non_curriculum":
        rule = ("For this study the manufacturers only let you play the "
                f"composition slot machine. Its payout for an arm {COMPOSITION_RULE}.")
    else:
        rule = ("In each casino you first play a slot machine from each of the two "
                f"companies, then a third combination machine whose payout for an arm {COMPOSITION_RULE}.")
    return (
        "You are a gambler visiting the fictional town of Bandit City. Over the session you "
        "visit a series of casinos and play slot machines, trying to win as many coins as "
        "possible. Every slot machine is made by one of two companies, Blue Lagoon and Green "
        "Geeks, and all machines from the same company pay out according to the same hidden "
        "pattern (you are not told which company has which pattern, so you learn it by playing). "
        "Each slot machine has six buttons in a row, labeled S, D, F, J, K, L. On every trial you "
        "press exactly one button to play that arm and you win some coins. "
        + rule + " "
        "On each trial, press the letter of the arm you want to play: S, D, F, J, K, or L."
    )


class CompositionalBandit:
    """Zero-shot compositional bandit, Experiment 2 (change-point rule) of
    Jagadish, Binz, Saanum, Wang & Schulz (2023), "Zero-shot compositional
    reasoning in a reinforcement learning setting", PsyArXiv; repo exp1.csv.

    Design (Materials and Methods > Task, p. 12, eqs 1-3 and 5): a 6-arm bandit
    sub-task pays r = y(arm) + N(0, 0.1) on each trial. Base reward functions
    are linear, y = w(2a/5 - 1) + b + zeta with w~U(-2.5,2.5), b~U(2.5,7.5),
    zeta~N(0,0.2), labeled pos/neg by the sign of w; and periodic,
    y = A|sin(0.5*pi*(a - phi))| + b + zeta with A~U(0,7.5), phi in {0,1}
    (0 = odd arms peak, 1 = even arms peak), b~U(0,A/1.4), zeta~N(0,0.2). The
    third sub-task of each curriculum task composes the two functions with the
    change-point rule (eq 5), y = [first half (arms 0-2), second half
    (arms 3-5)], where the order of the two halves is randomized per
    participant (the `rewardorder` flag; composition name [first][second], so
    rewardorder = 0 iff the first half is linear). Per participant one of
    compositional/loocompositional/noncompositional is drawn, and the pos/neg
    and even/odd orders are shuffled. 20 tasks per session (non-curriculum:
    only the composition machine).

    ASSUMPTION: low-slope / small-amplitude exclusion. The paper notes the
    function families were filtered to drop very low-slope linear and very
    small-amplitude periodic functions, but the thresholds are unpublished.
    The shipped env corpus has min |w| ~ 0.28; this simulator rejects
    |w| < 0.2 and A < 0.5.
    ASSUMPTION: the per-trial reward floor at 0 (reward = max(0, y + N(0,0.1)))
    is taken from the original task code (compositionalbandit.js), which the
    paper's eq 1 does not state.
    ASSUMPTION: reward functions are regenerated per (task, sub-task) from the
    paper's distributions rather than drawn from the shipped env JSON corpus,
    but with the same generative families and noise levels.
    """

    def __init__(self):
        self.name = "jagadish_2023_zeroshot_exp1"
        self.num_arms = 6
        self.trials_per_subtask = 5
        self.num_tasks = 20
        self.reward_sd = 0.1
        self.function_sd = 0.2
        self.rule = "changepoint"

    # ---- generative reward functions (paper eqs 2-3) ----
    def _linear_y(self, label):
        while True:
            w = np.random.uniform(-2.5, 2.5)
            if (w > 0) == (label == "pos") and abs(w) >= 0.2:
                break
        b = np.random.uniform(2.5, 7.5)
        a = np.arange(self.num_arms)
        y = w * (2.0 * a / (self.num_arms - 1) - 1.0) + b + np.random.normal(0.0, self.function_sd, self.num_arms)
        return y

    def _periodic_y(self, label):
        while True:
            amp = np.random.uniform(0.0, 7.5)
            if amp >= 0.5:
                break
        phase = 0 if label == "odd" else 1
        b = np.random.uniform(0.0, amp / 1.4)
        a = np.arange(self.num_arms)
        y = amp * np.abs(np.sin(np.pi / 2.0 * (a - phase))) + b + np.random.normal(0.0, self.function_sd, self.num_arms)
        return y

    def _composed_y(self, y_lin, y_per, lin, per, rewardorder):
        if rewardorder == 0:                 # linear first, periodic second
            name, y = lin + per, np.concatenate([y_lin[:3], y_per[3:]])
        else:                                # periodic first, linear second
            name, y = per + lin, np.concatenate([y_per[:3], y_lin[3:]])
        return name, y

    # ---- schedule (original task code, cond generation) ----
    def _schedule(self):
        linstruc = ["pos", "neg"]
        np.random.shuffle(linstruc)
        perstruc = ["even", "odd"]
        np.random.shuffle(perstruc)
        combos = [(l, p) for l in linstruc for p in perstruc]
        cond = str(np.random.choice(["compositional", "loocompositional", "noncompositional"]))
        if cond == "compositional":
            all_tasks = list(combos) * 5                      # 4 reps + 1 eval set
            train, ev = all_tasks[:16], all_tasks[16:]
            np.random.shuffle(train)
            np.random.shuffle(ev)
            tasks = train + ev
            eval_set = list(ev)
        elif cond == "loocompositional":
            all_tasks = []
            for l in linstruc:                                # hold out the last combo
                for p in perstruc:
                    for _ in range(6):
                        all_tasks.append((l, p))
            train = all_tasks[:18]
            ev = [all_tasks[18]]
            np.random.shuffle(train)
            tasks = list(train)
            tasks.append(train[0])                            # extra duplicate task
            tasks += ev
            eval_set = list(ev)
        else:                                                 # noncompositional
            all_tasks = list(combos) * 5
            train, ev = all_tasks[:16], all_tasks[16:]
            np.random.shuffle(train)
            np.random.shuffle(ev)
            tasks = train + ev
            eval_set = list(ev)
        return tasks, eval_set, cond

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            tasks, eval_set, cond = self._schedule()
            phase = "non_curriculum" if cond == "noncompositional" else "curriculum"
            curriculum = phase == "curriculum"
            rewardorder = int(np.random.choice([0, 1]))
            prompt = _intro(phase) + "\n"
            for t, (lin, per) in enumerate(tasks):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                y_lin = self._linear_y(lin)
                y_per = self._periodic_y(per)
                com, y_com = self._composed_y(y_lin, y_per, lin, per, rewardorder)
                if curriculum:
                    subtasks = [(lin, y_lin), (per, y_per), (com, y_com)]
                else:
                    subtasks = [(com, y_com)]
                for si, (label, y) in enumerate(subtasks):
                    task_id = t * len(subtasks) + si
                    subtask = si if curriculum else 2
                    task = t
                    maxr = float(np.max(y))
                    best = int(np.argmax(y))
                    env = f"envs/changepoint/{com}/{label}{np.random.randint(0, 100)}.json"
                    composition = json.dumps([lin, per, com]) if curriculum else json.dumps([com])
                    for trial in range(self.trials_per_subtask):
                        prompt += f"\nCasino {task}, machine {subtask + 1}: You press [HUMAN_RESPONSE]"
                        letter = str(agent(prompt, choice_options=ARMS))
                        response = ARMS.index(letter)
                        reward = max(0.0, float(y[response]) + np.random.normal(0.0, self.reward_sd))
                        prompt += f"{letter}[/HUMAN_RESPONSE] and win {reward:.2f} coins."
                        rows.append({
                            "participant_id": f"P{participant:03d}",
                            "task_id": task_id,
                            "trial": trial,
                            "response": response,
                            "reward": reward,
                            "regret": float(maxr - y[response]),
                            "condition": label,
                            "composition": composition,
                            "task": task,
                            "subtask": subtask,
                            "phase": phase,
                            "experiment": cond,
                            "rewardorder": rewardorder,
                            "maxreward": maxr,
                            "bestoption": best,
                            "env": env,
                            "eval": json.dumps(
                                [([l, p, (l + p) if rewardorder == 0 else (p + l)]) if curriculum else [l + p if rewardorder == 0 else p + l]
                                 for l, p in eval_set]),
                        })
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "task_id", "trial", "response", "reward",
            "regret", "condition", "composition", "task", "subtask", "phase",
            "experiment", "rewardorder", "maxreward", "bestoption", "env", "eval",
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

    task = CompositionalBandit()
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