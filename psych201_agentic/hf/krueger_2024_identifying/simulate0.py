# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/krueger_2024_identifying``
(Experiment 1), format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import json

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (Experiment 1 has no EV display).
INSTRUCTIONS = (
    "You are choosing between gambles to earn points. Your bonus is $0.01 for "
    "every 5 points you earn.\n"
    "On each round, 6 gambles labeled A, B, C, D, E, F (left to right) are on "
    "offer. Each gamble pays off in one of 4 possible outcomes, numbered 1 to 4 "
    "from top to bottom. Each outcome has a chance of occurring, shown as a "
    "percentage. The payoff of each gamble under each outcome is shown in a "
    "cell of the table, but all cells start hidden.\n"
    "To reveal a cell, type its label: the gamble letter followed by the "
    "outcome number (e.g. A1 is gamble A under outcome 1). Each reveal costs "
    "{cost}. Revealed cells stay visible for the rest of the round, and "
    "you may reveal as many or as few as you like, in any order.\n"
    "When you are ready, choose a gamble by typing its letter: A, B, C, D, E, "
    "or F. The outcome is then drawn at random according to the chances, and "
    "you earn that gamble's payoff for that outcome minus the {cost} "
    "you paid for each reveal."
)

OPEN = "[HUMAN_RESPONSE]"
CLOSE = "[/HUMAN_RESPONSE]"

GAMBLES = ["A", "B", "C", "D", "E", "F"]

# Design (4.1 "Experiment 1: Evaluating the model predictions", Methods,
# p. 23; 3.1 "The Mouselab paradigm", pp. 15-16): a 4-outcome x 6-gamble
# mouselab risky-choice task with between-subjects 2x5x5 factorial conditions.
# Participants do instruction/practice blocks then 20 test trials; each trial
# reveals payoff cells at a per-click cost, then picks a gamble and the outcome
# is drawn. Payoffs ~ N(0, sigma^2); outcome probabilities ~ Dirichlet(alpha);
# click cost lambda. No expected-value display in Experiment 1.
# trial counts: instruct1=3, instruct2=5, instruct3=3, test=20 (31 total).
SIGMA_SET = [75, 150]
ALPHA_SET = [10 ** -1.0, 10 ** -0.5, 10 ** 0.0, 10 ** 0.5, 10 ** 1.0]
COST_SET = [0, 1, 2, 4, 8]


def _num(v):
    return int(round(v))


def _points(n):
    return f"{n} point" if n == 1 else f"{n} points"


def _chances(probs):
    return ", ".join(f"{i}:{_num(p * 100)}%" for i, p in enumerate(probs, 1))


def _cell(idx):
    col, row = idx % 6, idx // 6
    return chr(ord("A") + col), row + 1


def _token(idx):
    letter, onum = _cell(idx)
    return f"{letter}{onum}"


def _token_to_idx(token):
    return (int(token[1]) - 1) * 6 + (ord(token[0]) - ord("A"))


def _integerize(probs, total=100):
    counts = (np.asarray(probs) * total)
    out = np.floor(counts).astype(int)
    rem = total - out.sum()
    order = np.argsort(counts - out)[::-1][:rem]
    out[order] += 1
    return out


class MouselabExperiment1:
    """Experiment 1 of Krueger, Callaway, Gul, Griffiths & Lieder (2024),
    "Identifying resource-rational heuristics for risky choice", Psychological
    Review, 131(4), 905-951.

    Design (Methods, p. 23; Mouselab paradigm, pp. 15-16): each of 31 trials
    (3 practice blocks of 3/5/3 + 20 test) presents a 4x6 payoff matrix (4
    outcomes x 6 gambles). Gambles labeled A-F, outcomes 1-4, cells A1..F4.
    Payoffs drawn from N(0, sigma^2) (sigma in {75,150}) and rounded to
    integers; outcome probabilities drawn from Dirichlet(alpha*1) with alpha in
    {1e-1,1e-.5,1,1e.5,1e1} and rendered as integer percentages of a 100-ball
    bin. Click cost lambda in {0,1,2,4,8}. These three parameters (stakes,
    dispersion, cost) are between-subjects, drawn per participant.

    ASSUMPTION: the simulator's uniform-random "agent" draws a per-trial number
    of cell reveals k ~ Uniform{0..12} (the harness decides frugality) and then
    picks which specific unrevealed cells to reveal uniformly at random; the
    final gamble is chosen uniformly from A-F. The real data's click sequences
    come from participants' learned policies; the exact count/order are not
    recoverable as a generative process, so a uniform draw is used.

    ASSUMPTION: outcome probabilities are integerized to 100 balls via the
    largest-remainder method on the Dirichlet sample (data store p*100 as
    integers summing to 100).

    The DataFrame matches exp0.csv minus unproducible columns (rt,
    time_elapsed, click_times, problem_id, bonus, total_time, start_time,
    browser, version, gender, age, education, wage, pass_*, instruct_time,
    params). flag is left empty (dominating-gamble trials are not simulated).
    """

    def __init__(self):
        self.name = "krueger_2024_identifying_exp0"
        self.phases = [
            (0, "instruct1", 3),
            (1, "instruct2", 5),
            (2, "instruct3", 3),
            (3, "test", 20),
        ]
        self.sigma_set = SIGMA_SET
        self.alpha_set = ALPHA_SET
        self.cost_set = COST_SET
        self.max_reveals = 12

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            sigma = int(np.random.choice(self.sigma_set))
            alpha = float(np.random.choice(self.alpha_set))
            cost = int(np.random.choice(self.cost_set))
            prompt = INSTRUCTIONS.format(cost=_points(cost))
            trial = 0
            for block, phase, n_trials in self.phases:
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                prompt += f"\n{_phase_header(phase)}"
                for _ti in range(n_trials):
                    mat = self._payoff_matrix(sigma)
                    probs = self._probabilities(alpha)
                    prompt += f"\nTrial {trial + 1}. Chances: {_chances(probs)}."
                    clicks, unrevealed = [], set(range(24))
                    k = np.random.randint(0, self.max_reveals + 1)
                    for _ in range(k):
                        options = sorted(_token(c) for c in unrevealed)
                        prompt += f"\nYou reveal {OPEN}"
                        tok = agent(prompt, choice_options=options)
                        idx = _token_to_idx(tok)
                        letter, onum = _cell(idx)
                        val = mat[onum - 1][ord(letter) - ord("A")]
                        prompt += f"{tok}{CLOSE}. {tok} shows {val}."
                        clicks.append(idx)
                        unrevealed.discard(idx)
                    prompt += f"\nYou choose gamble {OPEN}"
                    resp = agent(prompt, choice_options=GAMBLES)
                    prompt += f"{resp}{CLOSE}."
                    response = GAMBLES.index(resp)
                    payoff_index = int(np.random.choice(4, p=probs))
                    payoff_value = mat[payoff_index][response]
                    click_cost = cost * len(clicks)
                    net = payoff_value - click_cost
                    outcome = payoff_index + 1
                    if click_cost > 0:
                        prompt += (
                            f"\nOutcome {outcome} occurs. Your gamble pays "
                            f"{payoff_value} points. Net: {net} points (payoff "
                            f"minus {_points(click_cost)} for reveals)."
                        )
                    else:
                        prompt += (
                            f"\nOutcome {outcome} occurs. Your gamble pays "
                            f"{payoff_value} points. Net: {net} points."
                        )
                    rows.append({
                        "participant_id": participant,
                        "trial": trial,
                        "response": response,
                        "trial_type": "mouselab",
                        "click_cost": click_cost,
                        "probabilities": json.dumps(probs),
                        "cost": cost,
                        "payoff_index": payoff_index,
                        "net_payoff": net,
                        "payoff_value": payoff_value,
                        "payoff_matrix": json.dumps(mat),
                        "clicks": json.dumps(clicks),
                        "flag": "",
                        "block": block,
                        "trial_index": _ti,
                        "sigma": sigma,
                        "alpha": alpha,
                        "mu": 0,
                        "phase": phase,
                    })
                    trial += 1
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "trial_type", "click_cost",
            "probabilities", "cost", "payoff_index", "net_payoff",
            "payoff_value", "payoff_matrix", "clicks", "flag", "block",
            "trial_index", "sigma", "alpha", "mu", "phase",
        ])
        return df, prompts

    def _payoff_matrix(self, sigma):
        vals = np.round(np.random.normal(0.0, sigma, size=24)).astype(int)
        return vals.reshape(4, 6).tolist()

    def _probabilities(self, alpha):
        raw = np.random.dirichlet(np.full(4, alpha))
        counts = _integerize(raw, 100)
        return (counts / 100.0).tolist()


def _phase_header(phase):
    return {
        "instruct1": "Instruction block 1 (practice):",
        "instruct2": "Instruction block 2 (practice):",
        "instruct3": "Instruction block 3 (practice):",
        "test": "Test block:",
    }[phase]


def _random_agent(prompt, choice_options):
    return str(np.random.choice(list(choice_options)))


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

    task = MouselabExperiment1()
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