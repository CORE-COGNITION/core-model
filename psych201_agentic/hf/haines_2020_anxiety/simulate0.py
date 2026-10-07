# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/haines_2020_anxiety``, format-
identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp0), with the key-letter slots kept.
INSTRUCTIONS = (
    "In this study you complete a series of choices about money. "
    "Each trial shows you two reward options side by side. "
    "In the main part of the task the left option is a smaller reward available "
    "immediately (now), and the right option is a larger reward available only "
    "after a delay (later). You press the key {left_key} to choose the option on "
    "the left, or the key {right_key} to choose the option on the right. "
    "There are no right or wrong answers; pick the option you would genuinely "
    "prefer. The full session also includes practice and staircase trials with "
    "the same key layout."
)

# Delay set (in weeks) recovered from the main ADO trials of exp0.csv.
DELAYS = [0.43, 0.71, 1.0, 2.0, 3.0, 4.3, 6.44, 8.6, 10.8, 12.9, 17.2,
          21.5, 26.0, 52.0, 104.0, 156.0, 260.0, 520.0]


def fmt_money(dollars):
    # amounts are in dollars (the larger-later reward of the ADO trials is $800)
    if dollars is None:
        return None
    if abs(dollars - round(dollars)) < 1e-9:
        return f"${round(dollars)}"
    return f"${dollars:.2f}"


def _plural(x, unit):
    x = round(x, 1)
    x = int(x) if abs(x - round(x)) < 1e-9 else x
    return f"{x} {unit}{'s' if x != 1 else ''}"


def fmt_delay(weeks):
    # delays are in weeks (0.43 = 3 days, 4.3 = 1 month, 52 = 1 year, 520 = 10 years)
    if weeks is None:
        return None
    if weeks < 1:
        return _plural(round(weeks * 7), "day")
    if weeks < 3.5:
        return _plural(round(weeks), "week")
    if weeks < 52:
        return _plural(round(weeks / 4.33 * 2) / 2, "month")   # nearest half month
    return _plural(weeks / 52, "year")


def fmt_option(value, time):
    if time is None:
        return value
    if time == 0:
        return f"{value} now"
    return f"{value} in {fmt_delay(time)}"


class DelayDiscountingTask:
    """Delay-discounting task of Haines et al. (2020), "Anxiety Modulates
    Preference for Immediate Rewards Among Trait-Impulsive Individuals", Clinical
    Psychological Science, 8(6), 1017-1036.

    Design (Method, "Delay discounting", pp. 1019-1020): on each trial the
    participant chooses between a smaller-sooner reward (SS, left, immediate)
    and a larger-later reward (LL, right, delayed). Reward amounts and delays
    were titrated trial-by-trial with an adaptive ADO algorithm (Ahn et al.,
    2020); responses are binary (0 = SS, 1 = LL). One session = practice
    warmups, then two blocks of ADO main trials, then staircase trials. Three
    samples (MTurk online, student replication, SUD patients); the MTurk
    session (the most common) has practice + two ~20-trial ADO sessions and no
    staircase.

    ASSUMPTION: the ADO algorithm (Ahn et al., 2020) that selects each trial's
    SS amount and LL delay is not recoverable from the paper, the data-source
    repo (R/Stan analysis code only), or exp0.csv. As in the js-experiment
    build, this simulator draws each main/practice trial's SS amount and LL
    delay uniformly at random from the recovered design space instead. The SS
    amount is a multiple of $10 in [$10, $790]; the LL amount is the fixed $800;
    the LL delay (in weeks) is drawn from the delay set observed in the main
    ADO trials. The trial/phase/block structure (practice + two ADO main
    blocks) mirrors a typical MTurk participant.

    ASSUMPTION: sample is fixed to ``mturk`` and survey columns (BIS-11, STAI,
    AUDIT, DAST, demographics) are dropped — a text simulator cannot generate
    them. Only trial-level columns are produced.

    The DataFrame matches exp0.csv minus the survey columns.
    """

    def __init__(self):
        self.name = "haines_2020_anxiety_exp0"
        self.right_value = 800.0          # LL always $800
        self.practice_trials = 4          # practice warmup trials, block 0
        self.ado_blocks = 2               # two ADO main blocks
        self.ado_trials = 20              # trials per ADO block
        self.ss_options = np.arange(10, 791, 10).astype(float)   # $10..$790

    def _draw_trial(self):
        # SS amount in [10, 790]; LL fixed at 800; LL delay (weeks) from design set
        ss = float(np.random.choice(self.ss_options))
        delay = float(np.random.choice(DELAYS))
        return ss, delay

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            # per-participant key mapping, as in build_jsonl.py
            left_key, right_key = ("A", "B") if np.random.rand() < 0.5 else ("B", "A")
            prompt = INSTRUCTIONS.format(left_key=left_key, right_key=right_key) + "\n"
            trials = []   # list of dicts, narrated in build's sort order

            # practice trials, block 0
            for tn in range(self.practice_trials):
                ss, delay = self._draw_trial()
                trials.append({"block": 0, "trialNum": tn, "phase": "practice",
                               "leftValue": ss, "rightTime": delay})
            # ADO main trials: block 0 (tn 0..19) and block 1 (tn 0..19)
            for b in range(self.ado_blocks):
                for tn in range(self.ado_trials):
                    ss, delay = self._draw_trial()
                    trials.append({"block": b, "trialNum": tn, "phase": "main",
                                   "leftValue": ss, "rightTime": delay})

            # narration and rows in session order (practice, then the ADO blocks), as
            # build_jsonl.py narrates by `trial`
            trial_idx = 0
            for t in trials:
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                left_v = fmt_money(t["leftValue"])
                right_v = fmt_money(self.right_value)
                left_t, right_t = 0.0, t["rightTime"]
                if left_v and right_v and left_t is not None and right_t is not None:
                    detail = f"you get {fmt_option(left_v, left_t)} or {fmt_option(right_v, right_t)}"
                elif left_v and right_v:
                    detail = f"the left option is {left_v} and the right option is {right_v}"
                elif left_v and right_v is None:
                    detail = f"the left option is {left_v} and the right option is unavailable"
                else:
                    detail = "the two reward options are not recorded"

                prompt += f"You compare: {detail}. You press [HUMAN_RESPONSE]"
                letter = agent(prompt, choice_options=[left_key, right_key])
                response = 0 if letter == left_key else 1
                prompt += f"{letter}[/HUMAN_RESPONSE].\n"
                rows.append({
                    "participant_id": f"P{participant:03d}", "trial": trial_idx,
                    "response": int(response), "trialNum": float(t["trialNum"]),
                    "matrixIndex": float(np.random.randint(0, 1200)),
                    "leftValue": t["leftValue"], "leftTime": 0.0,
                    "rightValue": self.right_value, "rightTime": t["rightTime"],
                    "phase": t["phase"], "block": t["block"], "sample": "mturk",
                })
                trial_idx += 1
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "trialNum", "matrixIndex",
            "leftValue", "leftTime", "rightValue", "rightTime", "phase", "block", "sample",
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

    task = DelayDiscountingTask()
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