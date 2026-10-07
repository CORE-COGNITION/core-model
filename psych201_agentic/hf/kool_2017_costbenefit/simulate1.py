# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 of ``Hugging-Brain/kool_2017_costbenefit``,
format-identical to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or
import the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

EXP1_INSTR = (
    "You pilot a spaceship to a planet where aliens mine space treasure. At the "
    "start of every round a cue sets the stakes: points earned are multiplied by 1 "
    "(low) or by 5 (high). First you choose between two spaceships on screen: one "
    "flies to the red planet and the other to the purple planet, but each "
    "spaceship reaches one planet more often (70%) than the other (30%). "
    "Press F for the left spaceship and J for the right. On the planet you then "
    "choose between two aliens who work in different space mines: one is in a good "
    "spot and is more likely to pay out a piece of space treasure, the other in a "
    "bad spot and less likely. Press F for the left alien and J for the right. On "
    "each round you may win a piece of space treasure, worth 1 point or 5 "
    "depending on the stakes. Your running score is always shown in the top-right "
    "corner."
)

COLS = ["participant_id", "trial", "block", "stage", "phase", "state",
        "response", "valid", "reward", "stake", "score", "practice",
        "stim_left", "stim_right", "state2", "win",
        "p_win_state1_action1", "p_win_state1_action2",
        "p_win_state2_action2", "p_win_state2_action2_1"]


def _clip(p):
    """Clip a drifting P(win) into the paper's [0.25, 0.75] bounds."""
    return min(max(p, 0.25), 0.75)


def _key(resp):
    return "F" if resp == 0 else "J"


class DawTwoStepCostBenefitExp1:
    """Experiment 2 of Kool, Gershman & Cushman (2017), "Cost-benefit
    arbitration between multiple reinforcement-learning systems",
    Psychological Science, 28(9), 1321-1333.

    Design (Experiment 2, Materials and procedure, p. 1329-1331; Fig. 5): the
    Daw (2011) two-step task. A single first-stage state offers a choice between
    two spaceships (IDs 1,2); each leads to one planet 70% (common) and the
    other 30% (rare), with spaceship 1 -> planet 1 and spaceship 2 -> planet 2
    as the common transitions. On the reached planet the participant chooses
    between two aliens (IDs 1,2) that each pay one piece of treasure with a
    drifting probability bounded in [0.25, 0.75] (Gaussian random walk,
    mean 0, sigma 0.025; init pairs complementary, good drawn from
    {0.4, 0.6, 0.75}). A per-trial stake cue (x1 or x5, 50% each) multiplies
    the points (1 piece won = 1 or 5 points). 25 practice + 200 test trials,
    no response deadline in practice, 1500 ms in test for both choices.

    DataFrame matches exp1.csv minus demographics / model-fit / RT / keycode /
    raw-vs-derived duplicates / timing columns.

    ASSUMPTION: in the shipped data the practice phase always has stake 1; test
    stakes are ~48% high.
    ASSUMPTION: stage-1 timeouts (294) and stage-2 no-keypress trials (823)
    occur only in the test phase; this simulator uses the same per-trial rates
    (294/(100*200) and 823/(100*200-294)). Both leave the round rewardless and
    the running score unchanged.
    ASSUMPTION: ``score`` resets at the practice -> test boundary (per-phase
    total, matching exp1.csv); it increments by ``win * stake`` on a valid
    second-stage win.
    ASSUMPTION: the two second-stage win probabilities (and the two stage-1
    probabilities) drift independently (near-complementary at init but not
    strictly so across trials, matching exp1.csv).
    """

    def __init__(self):
        self.name = "kool_2017_costbenefit_exp1"
        self.num_practice = 25
        self.num_test = 200
        self.common_planet = {1: 1, 2: 2}
        self.p_common = 0.7
        self.p_drift = 0.025
        self.p_init_good = [0.4, 0.6, 0.75]
        self.p_stage1_timeout = 294.0 / (100 * 200)
        self.p_stage2_timeout = 823.0 / (100 * 200 - 294)

    def _init_p(self):
        g = float(np.random.choice(self.p_init_good))
        if np.random.rand() < 0.5:
            return g, 1.0 - g
        return 1.0 - g, g

    def _step_p(self, p):
        return _clip(p + np.random.normal(0.0, self.p_drift))

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            pid = f"Sub{participant + 1}"
            p1_a1, p1_a2 = self._init_p()
            p2_a2, p2_a2b = self._init_p()          # alien 1, alien 2 win prob
            lines = [EXP1_INSTR]
            score = 0
            carry_left, carry_right, carry_win = 1, 2, 0
            for b in range(self.num_practice + self.num_test):
                if max_chars is not None and len(" ".join(lines)) >= max_chars:
                    break
                phase = "practice" if b < self.num_practice else "test"
                practice = 1 if phase == "practice" else 0
                stake = 1 if phase == "practice" else (5 if np.random.rand() < 0.5 else 1)
                p1_a1 = self._step_p(p1_a1)
                p1_a2 = self._step_p(p1_a2)
                p2_a2 = self._step_p(p2_a2)
                p2_a2b = self._step_p(p2_a2b)
                pvals = (p1_a1, p1_a2, p2_a2, p2_a2b)
                s1_left, s1_right = (1, 2) if np.random.rand() < 0.5 else (2, 1)

                if phase == "test" and np.random.rand() < self.p_stage1_timeout:
                    lines.append(f"Stakes x{stake}. You fail to choose a spaceship "
                                 f"in time, so no round is played.")
                    rows.append(self._rec(pid, b, "stage1", phase, practice, stake,
                                          score, 0.0, np.nan, 0, np.nan, s1_left,
                                          s1_right, np.nan, carry_win, pvals))
                    rows.append(self._rec(pid, b, "stage2", phase, practice, stake,
                                          score, np.nan, np.nan, 0, np.nan,
                                          carry_left, carry_right, np.nan, carry_win,
                                          pvals))
                    continue

                lines.append(f"Stakes x{stake}. Two spaceships appear: Ship {s1_left} "
                             f"on the left and Ship {s1_right} on the right. You press "
                             f"[HUMAN_RESPONSE]")
                response1 = 0 if agent(" ".join(lines), choice_options=["F", "J"]) == "F" else 1
                lines[-1] += f"{_key(response1)}[/HUMAN_RESPONSE]."
                choice1 = s1_left if response1 == 0 else s1_right
                if np.random.rand() < self.p_common:
                    state2 = self.common_planet[choice1]
                else:
                    state2 = 3 - self.common_planet[choice1]
                s2_left, s2_right = (1, 2) if np.random.rand() < 0.5 else (2, 1)
                stage2_timed = phase == "test" and np.random.rand() < self.p_stage2_timeout

                if stage2_timed:
                    lines.append("On the planet you fail to choose an alien in time.")
                    rows.append(self._rec(pid, b, "stage1", phase, practice,
                                      stake, score, 0.0, response1, 1, np.nan,
                                      s1_left, s1_right, state2, carry_win, pvals))
                    rows.append(self._rec(pid, b, "stage2", phase, practice,
                                      stake, score, state2 - 1, np.nan, 0, np.nan,
                                      s2_left, s2_right, state2, carry_win, pvals))
                    continue

                lines.append(f"On Planet {state2}, two aliens appear: Alien {s2_left} "
                             f"on the left and Alien {s2_right} on the right. You press "
                             f"[HUMAN_RESPONSE]")
                response2 = 0 if agent(" ".join(lines), choice_options=["F", "J"]) == "F" else 1
                chosen2 = s2_left if response2 == 0 else s2_right
                p_win = p2_a2 if chosen2 == 1 else p2_a2b
                won = int(np.random.rand() < p_win)
                pts = won * stake
                score2 = score + pts
                outcome = (f"you win a piece of space treasure, +{pts} points"
                           if won else "you win no treasure")
                lines[-1] += (f"{_key(response2)}[/HUMAN_RESPONSE] and "
                              f"{outcome}. Your running score is {score2}.")
                rows.append(self._rec(pid, b, "stage1", phase, practice, stake,
                                      score, 0.0, response1, 1, np.nan, s1_left,
                                      s1_right, state2, won, pvals))
                rows.append(self._rec(pid, b, "stage2", phase, practice, stake,
                                      score2, state2 - 1, response2, 1, float(won),
                                      s2_left, s2_right, state2, won, pvals))
                carry_left, carry_right, carry_win = s2_left, s2_right, won
                score = score2
            prompts.append(" ".join(lines).strip())
        df = pd.DataFrame(rows, columns=COLS)
        return df, prompts

    def _rec(self, pid, b, stage, phase, practice, stake, score, state,
             response, valid, reward, stim_left, stim_right, state2, win, pvals):
        p1_a1, p1_a2, p2_a2, p2_a2b = pvals
        return {
            "participant_id": pid,
            "trial": 2 * b if stage == "stage1" else 2 * b + 1,
            "block": b, "stage": stage, "phase": phase, "state": state,
            "response": response, "valid": valid, "reward": reward,
            "stake": stake, "score": score, "practice": practice,
            "stim_left": stim_left, "stim_right": stim_right, "state2": state2,
            "win": win, "p_win_state1_action1": p1_a1,
            "p_win_state1_action2": p1_a2, "p_win_state2_action2": p2_a2,
            "p_win_state2_action2_1": p2_a2b}


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

    task = DawTwoStepCostBenefitExp1()
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
        first = p.split(".", 1)[0]
        print(f"participant {i} first line: {first}")
    print("=" * 78)
    print("first prompt, head:")
    print(prompts[0][:700])
    print("...")
    print("first prompt, tail:")
    print(prompts[0][-500:])


if __name__ == "__main__":
    main()