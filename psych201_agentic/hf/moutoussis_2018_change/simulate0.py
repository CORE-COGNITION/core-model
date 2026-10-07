# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/moutoussis_2018_change``, the
baseline session of Moutoussis et al. (2018), format-identical to the repo's
``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_gonogo), shared by both experiments.
INSTRUCTIONS = (
    "You are playing a game for real money. On each trial you see one of four "
    "abstract fractal patterns (cue A, cue B, cue C or cue D) on screen, then a "
    "target appears shortly afterwards. Your job is to decide whether to press the "
    "button (Go) or to withhold the press (NoGo). Each cue has a fixed, unknown rule "
    "about whether pressing is better, so you must learn the rules by trial and "
    "error as the game goes on; the right answers gradually sink in. The outcome "
    "probabilities are 80% and 20%, and you can win or lose money. "
    "To choose Go (press the button), type G. To choose NoGo (do not press), type N. "
    "After your choice you see the outcome.\n"
)

CUE_LABEL = {"win_go": "cue A", "win_nogo": "cue B",
             "lose_go": "cue C", "lose_nogo": "cue D"}

OUTCOME = {-1: "You lose money.", 0: "Nothing changes.", 1: "You win money."}

# condition_code: (label, dominant_response, dominant_outcome)
# dominant_response is the response (0=NoGo, 1=Go) that realises the dominant
# outcome with probability 0.8 (the wrong response realises it with 0.2);
# the alternative is the null outcome (0).
CONDITION = {
    1: ("win_go", 1, 1),
    2: ("lose_go", 0, -1),
    3: ("win_nogo", 0, 1),
    4: ("lose_nogo", 1, -1),
}

COLUMNS = [
    "participant_id", "trial", "task_id", "session", "condition_code", "condition",
    "response_cue1", "response_cue2", "sham", "target_position", "key_pressed",
    "response_raw", "target_display_duration", "reward", "valid", "response",
]


class GoNoGoTask:
    """Orthogonalised Go-NoGo task, Experiment 1 of Moutoussis et al. (2018),
    "Change, stability, and instability in the Pavlovian guidance of behaviour
    from adolescence to young adulthood", PLOS Comp Biol, 14, e1006679.

    Design (Methods, "The Go-NoGo task", pp. 15-16): a baseline session in which
    participants see four abstract fractal cues, each with a constant, unknown
    correct policy (Go or NoGo). If the correct decision is made the better of
    two outcomes is realised with probability 0.8; otherwise with 0.2. Each run
    is 144 trials (36 of each of the four conditions); 61 participants have a
    second run, the 6-month short follow-up session (session = short_follow_up).
    Outcome probabilities were 0.8 / 0.2 and subjects played for real money.

    The condition -> outcome mapping follows the paper (Methods p. 16) and
    exp0.csv: win_go realises +1 on Go with p=0.8 (else null); win_nogo realises
    +1 on NoGo with p=0.8; lose_go realises -1 on NoGo with p=0.8 (Go avoids the
    loss); lose_nogo realises -1 on Go with p=0.8. The outcome text ("win money"
    / "lose money") mirrors build_jsonl.py's OUTCOME map; the paper states no
    per-trial amount.

    ASSUMPTION: within a run the cue order is a uniform random permutation of
    exactly 36 trials per condition (matching the data's exact 36-per-condition
    counts); the exact serial order is random and unrecoverable, so it is drawn
    fresh per run.

    ASSUMPTION: premature cue presses (response_cue1) are iid Bernoulli with the
    experiment's empirical rate, uniform across conditions and trial positions
    (the data rate varies slightly by condition, 0.024-0.049).

    ASSUMPTION: all simulated trials are valid; the ~2% of data trials flagged
    invalid (source response_raw == 3) are dropped. This does not change the
    transcript text, which is identical for valid and invalid trials.

    ASSUMPTION: a second run (task_id 1, the short follow-up session) is drawn per
    participant with the empirical probability 61/817.

    The DataFrame mirrors exp0.csv minus the timing columns a text simulator
    cannot produce (cue_onset_time, cue_target_interval, target_onset_time,
    keypress_time, rt, outcome_onset_time, intertrial_interval).
    """

    def __init__(self):
        self.name = "moutoussis_2018_change_exp0"
        self.num_trials = 144
        self.trials_per_condition = 36
        self.win_prob = 0.8
        self.second_session_prob = 61 / 817
        self.premature_prob = 4462 / 126432

    def _one_run(self, agent, task_id, participant_id, rows, prompt):
        conds = []
        for code in CONDITION:
            conds += [code] * self.trials_per_condition
        np.random.shuffle(conds)
        prompt += f"Task {task_id + 1}.\n"
        for trial in range(self.num_trials):
            code = conds[trial]
            label, dominant_response, dominant_outcome = CONDITION[code]
            cue = CUE_LABEL[label]
            premature = np.random.rand() < self.premature_prob
            prompt += f"You see {cue}. "
            if premature:
                prompt += "You press the button prematurely during the cue. "
            prompt += "You press [HUMAN_RESPONSE]"
            letter = agent(prompt, choice_options=["G", "N"])
            resp = 1 if letter == "G" else 0
            p = self.win_prob if resp == dominant_response else 1 - self.win_prob
            reward = dominant_outcome if np.random.rand() < p else 0
            prompt += f"{letter}[/HUMAN_RESPONSE]. {OUTCOME[reward]}\n"
            rows.append({
                "participant_id": participant_id, "trial": trial, "task_id": task_id,
                "session": "baseline" if task_id == 0 else "short_follow_up",
                "condition_code": code, "condition": label,
                "response_cue1": int(premature), "response_cue2": 0, "sham": 0,
                "target_position": 1, "key_pressed": 71 if resp else 0,
                "response_raw": resp, "target_display_duration": 800.0,
                "reward": float(reward), "valid": 1, "response": resp,
            })
        return prompt

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            pid = f"P{participant:03d}"
            prompt = INSTRUCTIONS
            num_runs = 1 + (1 if np.random.rand() < self.second_session_prob else 0)
            for task_id in range(num_runs):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                prompt = self._one_run(agent, task_id, pid, rows, prompt)
            prompts.append(prompt.strip())
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

    task = GoNoGoTask()
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