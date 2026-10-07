# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 of ``Hugging-Brain/krueger_2024_identifying``
(Experiment 2), format-identical to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse
import json

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (Experiment 2 may show the EV display).
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

EV_INSTRUCTIONS = (
    "A running expected value for each gamble is displayed next to its letter "
    "and updates as you reveal cells. You must wait at least 20 seconds each "
    "round before choosing; a countdown timer shows the remaining time."
)

OPEN = "[HUMAN_RESPONSE]"
CLOSE = "[/HUMAN_RESPONSE]"

GAMBLES = ["A", "B", "C", "D", "E", "F"]

# Design (4.2 "Experiment 2: Reducing cognitive constraints", Methods,
# pp. 40-41): same mouselab task but a 2x2x2 between-subjects design
# (dispersion alpha in {10^-.5,10^.5}, cost in {1,4}, control vs experimental
# group). Stakes are low (sigma = 75). The experimental group shows the running
# subjective expected value of each gamble (Equation 3) and a 20-s time minimum.
# trial counts: instruct1=3, instruct2=3, instruct3=3, test=20 (29 total).
SIGMA = 75
ALPHA_SET = [10 ** -0.5, 10 ** 0.5]
COST_SET = [1, 4]
CONDITIONS = ["con", "exp"]


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


def _fmt_ev(evs):
    return ", ".join(f"{chr(ord('A') + i)}:{_num(v)}" for i, v in enumerate(evs))


def _integerize(probs, total=100):
    counts = (np.asarray(probs) * total)
    out = np.floor(counts).astype(int)
    rem = total - out.sum()
    order = np.argsort(counts - out)[::-1][:rem]
    out[order] += 1
    return out


class MouselabExperiment2:
    """Experiment 2 of Krueger, Callaway, Gul, Griffiths & Lieder (2024),
    "Identifying resource-rational heuristics for risky choice", Psychological
    Review, 131(4), 905-951.

    Design (Methods, pp. 40-41): 29 trials (practice blocks 3/3/3 + 20 test) of
    the same 4x6 (outcome x gamble) mouselab task. Between-subjects 2x2x2
    factorial: dispersion alpha in {10^-.5, 10^.5}, click cost in {1,4}, and
    control (con) vs experimental (exp) group. sigma = 75 throughout. In the
    exp group each trial shows a running expected-value display (Equation 3:
    EV_g = sum over revealed cells (o,g) of p(o)*v_o,g, unrevealed payoffs
    replaced by the prior mean 0) and enforces a 20-second minimum.

    ASSUMPTION: the simulator's uniform-random "agent" draws a per-trial number
    of cell reveals k ~ Uniform{0..12} (the harness decides frugality) and then
    picks which specific unrevealed cells to reveal uniformly at random; the
    final gamble is chosen uniformly from A-F. The real data's click sequences
    come from participants' learned policies; the exact count/order are not
    recoverable as a generative process, so a uniform draw is used.

    ASSUMPTION: outcome probabilities are integerized to 100 balls via the
    largest-remainder method on the Dirichlet sample (data store p*100 as
    integers summing to 100).

    The DataFrame matches exp1.csv minus unproducible columns (rt,
    time_elapsed, click_times, problem_id, bonus, total_time, start_time,
    browser, version, gender, age, education, wage, pass_*, instruct_time,
    params, shuffle_trials, n_comprehension, bonus_rate). revealed_points is
    dropped (it is derivable from payoff_matrix + clicks). flag is left empty
    (dominating-gamble trials are not simulated).
    """

    def __init__(self):
        self.name = "krueger_2024_identifying_exp1"
        self.phases = [
            (0, "instruct1", 3),
            (1, "instruct2", 3),
            (2, "instruct3", 3),
            (3, "test", 20),
        ]
        self.sigma = SIGMA
        self.alpha_set = ALPHA_SET
        self.cost_set = COST_SET
        self.conditions = CONDITIONS
        self.max_reveals = 12

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            alpha = float(np.random.choice(self.alpha_set))
            cost = int(np.random.choice(self.cost_set))
            condition = str(np.random.choice(self.conditions))
            show_ev = condition == "exp"
            display_ev = 1 if show_ev else 0
            min_trial_secs = float(20 if show_ev else 0)
            prompt = INSTRUCTIONS.format(cost=_points(cost))
            if show_ev:
                prompt += "\n" + EV_INSTRUCTIONS
            trial = 0
            for block, phase, n_trials in self.phases:
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                prompt += f"\n{_phase_header(phase)}"
                for _ti in range(n_trials):
                    mat = self._payoff_matrix()
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
                    evs = self._expected_values(mat, probs, clicks)
                    if show_ev:
                        prompt += f"\nExpected-value display: {_fmt_ev(evs)}."
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
                        "payoff_index": payoff_index,
                        "display_ev": display_ev,
                        "cost": cost,
                        "min_trial_secs": min_trial_secs,
                        "payoff_matrix": json.dumps(mat),
                        "net_payoff": net,
                        "clicks": json.dumps(clicks),
                        "probabilities": json.dumps(probs),
                        "payoff_value": payoff_value,
                        "click_cost": click_cost,
                        "e_vs": json.dumps(evs),
                        "flag": "",
                        "block": block,
                        "trial_index": _ti,
                        "sigma": self.sigma,
                        "alpha": alpha,
                        "mu": 0,
                        "phase": phase,
                        "condition": condition,
                    })
                    trial += 1
            prompts.append(prompt)
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "trial_type", "payoff_index",
            "display_ev", "cost", "min_trial_secs", "payoff_matrix", "net_payoff",
            "clicks", "probabilities", "payoff_value", "click_cost", "e_vs",
            "flag", "block", "trial_index", "sigma", "alpha", "mu", "phase",
            "condition",
        ])
        return df, prompts

    def _payoff_matrix(self):
        vals = np.round(np.random.normal(0.0, self.sigma, size=24)).astype(int)
        return vals.reshape(4, 6).tolist()

    def _probabilities(self, alpha):
        raw = np.random.dirichlet(np.full(4, alpha))
        counts = _integerize(raw, 100)
        return (counts / 100.0).tolist()

    def _expected_values(self, mat, probs, clicks):
        evs = [0.0] * 6
        for idx in clicks:
            o, g = idx // 6, idx % 6
            evs[g] += probs[o] * mat[o][g]
        return evs


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

    task = MouselabExperiment2()
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