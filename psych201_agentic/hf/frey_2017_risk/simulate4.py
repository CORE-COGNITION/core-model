# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp4 (Decisions From Experience) of
``Hugging-Brain/frey_2017_risk``, format-identical to the repo's
``transcripts4.jsonl``.

``uv run simulate4.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe_exp4); boxes are fixed A/B, so the
# final response is the A/B letter with no per-participant token mapping.
INSTRUCTIONS = (
    "In this task two boxes, A and B, contain unknown payoffs. You can draw (sample) "
    "outcomes from either box to learn what each tends to pay, then decide which box "
    "you prefer. Your choice may be paid for real. On each trial press A to choose "
    "box A, or B to choose box B.\n")

# The 8 gamble problems (Hertwig et al. 2004 rare-event gambles, gain and loss
# variants). Each entry: (gamble_lab, domain, A spec, B spec, rare box, rare value).
# A spec / B spec are lists of (outcome, probability); probabilities sum to 1.
# The rare box/value were recovered from dfe_samples.csv (the target rare event
# whose draws count toward ``rare_n``); the distributions were recovered from the
# same file by pooling all draws across participants.
GAMBLES = [
    ("he04_1", "gain", [(4, 0.8), (0, 0.2)], [(3, 1.0)], "A", 0),
    ("he04_2", "gain", [(4, 0.2), (0, 0.8)], [(3, 0.25), (0, 0.75)], "A", 4),
    ("he04_3", "loss", [(-3, 1.0)], [(-32, 0.1), (0, 0.9)], "B", -32),
    ("he04_4", "loss", [(-3, 1.0)], [(-4, 0.8), (0, 0.2)], "B", 0),
    ("he04_5", "gain", [(32, 0.1), (0, 0.9)], [(3, 1.0)], "A", 32),
    ("he04_6", "gain", [(32, 0.025), (0, 0.975)], [(3, 0.25), (0, 0.75)], "A", 32),
    ("he04_2inv", "loss", [(-3, 0.25), (0, 0.75)], [(-4, 0.2), (0, 0.8)], "B", -4),
    ("he04_6inv", "loss", [(-3, 0.25), (0, 0.75)], [(-32, 0.025), (0, 0.975)], "B", -32),
]

# Total-samples count model: negative binomial fit by method of moments to the
# observed per-trial sample counts (mean 26.4, var 362.5 -> r=2.07, p=0.073),
# drawn via a gamma-Poisson mixture.
NB_R = 2.07
NB_P = 0.073

# Per-gamble switching probability of the two-box sampling Markov chain,
# Beta(alpha, beta). The observed per-step switch rate is small (median ~0.04,
# mean ~0.11 for large sample counts), and zero-switch trials are essentially
# never seen once sample counts rise; an alpha>1 Beta keeps this behaviour
# (density 0 at 0, so both boxes always get sampled for large n).
SW_ALPHA = 1.5
SW_BETA = 12.0


def _fmt(x):
    x = float(x)
    return str(int(x)) if x == int(x) else f"{x:g}"


def _trim(v):
    return round(float(v), 2)


class DecisionsFromExperience:
    """Decisions from experience, exp4 of the Basel-Berlin Risk Study (Frey et
    al. 2017, Sci. Adv. 3, e1701381).

    Design (task 4 'Decisions from experience'): 8 rare-event gamble problems
    (Hertwig, Barron, Weber & Erev 2004), 4 gain and 4 loss (inverse) variants,
    each presenting two payoff boxes A and B. The participant freely draws
    (samples) outcomes from the boxes to learn their payoffs, then chooses one
    box. One trial is paid for real. Recorded per trial: number of samples,
    switches/switching rate, the experienced mean and variance of each box, the
    number of rare-event draws, and the final A/B choice.

    The experience is generated as follows: draw a total sample count n, run a
    two-state Markov chain over boxes (start box random), and draw each sample
    outcome from that box's true distribution; the experienced statistics are
    then computed exactly as in the source (sample mean, sample variance ddof=1,
    rounded to 2 decimals). Only the final A/B choice is a free response.

    ASSUMPTION: total samples per trial follow a negative binomial
    (r=2.07, p=0.073, method-of-moments fit to the observed marginal); the real
    sampling rule is free-form and not stated in the paper.

    ASSUMPTION: the box-choice sequence is a two-state Markov chain whose
    per-step switch probability is drawn per trial from Beta(1.5, 12) (mean
    ~0.11), matching the observed low per-step switch rate and the absence of
    zero-switch trials at large sample counts.

    ASSUMPTION: remainders of the real protocol fixed -- gamble presentation
    order is a random permutation per participant (the data show shuffled
    orders), location (Basel/Berlin) is drawn uniformly, and every participant
    completes all 8 gambles.

    The DataFrame matches exp4.csv minus the reaction-time columns ``rt`` and
    ``rt_sample``, which a text simulator cannot produce.
    """

    def __init__(self):
        self.name = "frey_2017_risk_exp4"
        self.gambles = GAMBLES
        self.nb_r = NB_R
        self.nb_p = NB_P
        self.sw_alpha = SW_ALPHA
        self.sw_beta = SW_BETA

    def _draw_outcome(self, spec):
        outs = np.array([o for o, _ in spec], dtype=float)
        probs = np.array([p for _, p in spec], dtype=float)
        return float(np.random.choice(outs, p=probs))

    def _ev_var(self, spec):
        ev = sum(o * p for o, p in spec)
        var = sum(p * (o - ev) ** 2 for o, p in spec)
        return ev, var

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        rng_sw = np.random
        for participant in tqdm(range(num_simulations)):
            location = str(np.random.choice(["Basel", "Berlin"]))
            order = rng_sw.permutation(len(self.gambles))
            prompt = INSTRUCTIONS
            for trial, gix in enumerate(order):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                lab, domain, spec_a, spec_b, rare_box, rare_val = self.gambles[gix]
                # total samples this trial
                lam = float(rng_sw.gamma(shape=self.nb_r, scale=(1.0 - self.nb_p) / self.nb_p))
                n = int(rng_sw.poisson(lam))
                # two-box sampling Markov chain
                p_sw = float(rng_sw.beta(self.sw_alpha, self.sw_beta))
                box = "A" if rng_sw.rand() < 0.5 else "B"
                seq = [box]
                switches = 0
                for i in range(1, n):
                    if rng_sw.rand() < p_sw:
                        box = "B" if box == "A" else "A"
                        switches += 1
                    seq.append(box)
                if n >= 30 and set(seq) != {"A", "B"}:
                    # real participants never sample a single box beyond ~28
                    # draws; force the last draw from the other box instead
                    other = "B" if seq[-1] == "A" else "A"
                    seq[-1] = other
                    switches += 1
                draws = {"A": [], "B": []}
                for b in seq:
                    draws[b].append(self._draw_outcome(spec_a if b == "A" else spec_b))
                a_out, b_out = draws["A"], draws["B"]
                a_mean = float(np.mean(a_out)) if a_out else np.nan
                b_mean = float(np.mean(b_out)) if b_out else np.nan
                a_var = float(np.var(a_out, ddof=1)) if len(a_out) > 1 else np.nan
                b_var = float(np.var(b_out, ddof=1)) if len(b_out) > 1 else np.nan
                a_mean = _trim(a_mean) if not np.isnan(a_mean) else np.nan
                b_mean = _trim(b_mean) if not np.isnan(b_mean) else np.nan
                a_var = _trim(a_var) if not np.isnan(a_var) else np.nan
                b_var = _trim(b_var) if not np.isnan(b_var) else np.nan
                rare_n = int(sum(1 for v in draws[rare_box] if v == rare_val))
                sw = switches if n > 1 else np.nan
                swrate = (switches / (n - 1)) if n > 1 else np.nan
                swrate = round(float(swrate), 2) if not np.isnan(swrate) else np.nan
                av = self._fmt_var(a_mean, a_var)
                bv = self._fmt_var(b_mean, b_var)
                sw_txt = str(int(sw)) if not np.isnan(sw) else "0"
                prompt += (f"You drew {n} samples, switching between the boxes {sw_txt} time(s). "
                           f"Box A outcomes {av}. Box B outcomes {bv}. "
                           f"You press [HUMAN_RESPONSE]")
                letter = str(agent(prompt, choice_options=["A", "B"]))
                assert letter in ("A", "B")
                prompt += f"{letter}[/HUMAN_RESPONSE].\n"
                ev_a, var_a = self._ev_var(spec_a)
                ev_b, var_b = self._ev_var(spec_b)
                h = int((ev_a > ev_b) if letter == "A" else (ev_b > ev_a))
                r = int((var_a > var_b) if letter == "A" else (var_b > var_a))
                hexp = self._strict(letter, a_mean, b_mean)
                rexp = self._strict(letter, a_var, b_var)
                rows.append({
                    "participant_id": participant, "trial": trial, "response": letter,
                    "location": location, "gamble_lab": lab, "domain": domain,
                    "gamble_ind": int(gix + 1), "samples": n, "switches": sw,
                    "swrate": swrate, "A_mean": a_mean, "A_var": a_var,
                    "B_mean": b_mean, "B_var": b_var, "rare_n": rare_n,
                    "H": h, "Hexp": hexp, "R": r, "Rexp": rexp, "decision": letter,
                })
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "trial", "response", "location", "gamble_lab", "domain",
            "gamble_ind", "samples", "switches", "swrate", "A_mean", "A_var",
            "B_mean", "B_var", "rare_n", "H", "Hexp", "R", "Rexp", "decision",
        ])
        df = df.astype({
            "participant_id": "int64", "trial": "int64", "gamble_ind": "int64",
            "samples": "int64", "rare_n": "int64", "H": "int64", "R": "int64",
        })
        for c in ["switches", "swrate", "A_mean", "A_var", "B_mean", "B_var",
                  "Hexp", "Rexp"]:
            df[c] = df[c].astype("float64")
        return df, prompts

    @staticmethod
    def _fmt_var(m, v):
        parts = []
        if not np.isnan(m):
            parts.append(f"averaged {_fmt(m)}")
        if not np.isnan(v):
            parts.append(f"variance {_fmt(v)}")
        if not parts:
            return "you saw no outcomes from this box"
        return " and ".join(parts)

    @staticmethod
    def _strict(letter, m_chosen, m_other):
        if np.isnan(m_chosen) or np.isnan(m_other) or m_chosen == m_other:
            return np.nan
        return 1.0 if m_chosen > m_other else 0.0


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

    task = DecisionsFromExperience()
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