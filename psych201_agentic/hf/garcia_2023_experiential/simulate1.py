
# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 of ``Hugging-Brain/garcia_2023_experiential``,
format-identical to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py (transcribe / PHASE_GUIDE / helpers).
WELCOME = (
    "Welcome. In this decision-making task, each trial presents options that can win or "
    "lose you points. Options are of three kinds: experiential symbols (numbered; you learn their "
    "value from the outcomes they deliver; each session uses a new set of symbols), symbolic lotteries (a pie chart stating an "
    "explicit win probability), and ambiguous options (value hidden). In choice phases you "
    "are shown two options: press A to choose option 1, or press B to choose option 2."
)
NO_OUTCOME = " Outcomes are not shown in this phase, but your choices still count toward your points."
PHASE_GUIDE = {
    "LE": "This phase shows two experiential symbols; you learn which one is better from the outcomes they give you.",
    "ES": "This phase shows one experiential symbol and one symbolic lottery; choose the option you prefer." + NO_OUTCOME,
    "EE": "This phase shows two experiential symbols; choose based on what you have learned about them." + NO_OUTCOME,
    "EA": "This phase pairs an experiential symbol with an ambiguous option whose value is hidden." + NO_OUTCOME,
    "SA": "This phase pairs a symbolic lottery with an ambiguous option whose value is hidden." + NO_OUTCOME,
    "SP": ("This phase shows one option at a time. Report your estimate of its win probability as a number "
           "from 0 to 100 in steps of 5 (0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, "
           "85, 90, 95 or 100). The outcome of your answer is not shown."),
}


def _pct(p):
    if pd.isna(p):
        return None
    return f"{int(round(float(p) * 100))}%"


def _desc(opt, p, labels=None):
    opt = str(opt) if not pd.isna(opt) else ""
    if opt == "S":
        return f"a symbolic lottery with a {_pct(p)} win probability"
    if opt == "A":
        return "an ambiguous option with its value hidden"
    if labels is not None and not pd.isna(p):
        k = labels.get(round(float(p), 2))
        if k is not None:
            return f"experiential symbol {k}"
    return "an experiential symbol you have learned about"


def _outcome(reward):
    if pd.isna(reward):
        return ""
    if float(reward) > 0:
        return " You win 1 point."
    return " You lose 1 point."


def _cf_outcome(cfout):
    if pd.isna(cfout):
        return ""
    if float(cfout) > 0:
        return " The other option would have won 1 point."
    return " The other option would have lost 1 point."


def _ev(p):
    return 2.0 * float(p) - 1.0 if not pd.isna(p) else np.nan


class GarciaExperiential:
    """Garcia et al. (2023), exp1: blocked LE design.

    Design from Garcia et al. (2023), "The impassable gap between experiential
    and symbolic values", Nature Human Behaviour 7: 611-626 (preprint
    https://doi.org/10.21203/rs.3.rs-1361189/v1; Methods/Procedure + data CSVs).
    Two-option bandit. The main (analyzed) session starts with a learning (LE)
    phase of 120 trials across the experiment's fixed E-option pairs
    (experiential symbols, +/-1 point feedback, p(win) given by each pair).
    Transfer phases then offer hybrid choices: ES = experiential vs symbolic
    lottery, EE = experiential vs experiential, and (exps 6-7) EA/SA =
    experiential/symbolic vs an ambiguous hidden-value option. A final SP phase
    asks for stated win-probability estimates (0-100). Across experiments the
    E-value ladder and the symbolic-lottery grid differ (config below).

    The simulator reproduces the main analyzed session session. Each participant is a fresh
    schedule drawn from the experiment's fixed stimulus grid; choices come from
    the ``agent``; outcomes are Bernoulli draws at the chosen option's p(win).

    ASSUMPTION: only the main analyzed test session is built (training sessions
    -1/-2 and the second test session of exps 5-8 are omitted), matching the
    scope of this repo's js-build (README ``## Online experiment``).
    ASSUMPTION: LE/EE/ES/EA/SA trial order, E-symbol-to-value assignment and
    left/right reversal are randomized per participant (the source does not
    record symbol identity); symbolic lotteries are exact (described by p).
    ASSUMPTION: EE = ordered pairs of distinct E-values ({ee_total} = n*(n-1) for
    the 8-value ladder); the ES grid = full crossing of E-values x the grid read
    from the CSVs; the SP item list = all E-values (as E) plus the ES lottery
    grid (as S), rounded.
    ASSUMPTION: EA/SA ambiguous option (op2='A') carries a hidden value drawn
    from the experiment's grids; its p is not narrated.
    ASSUMPTION: ES catch trials = choices between two lotteries drawn from the
    experiment's catch grids (catch_p1 x catch_p2; Methods: one lottery obviously
    better), coded op1='E', catch_trial=1 as in the source; SP ratings of an
    S-lottery item are catch trials; SP reward/correct use |estimate/100 - p| <= 0.1.
    Outcomes are narrated only in the LE phase (chosen option; plus the unchosen
    option's outcome when complete_feedback, i.e. from exp2 on), never in the
    ES/EE/EA/SA/SP phases (Methods: no feedback there); rewards are still recorded.
    E-symbols are named "experiential symbol <k>", k a per-participant shuffle of
    1..n over the E-values (same seeding as build_jsonl.py).
    """

    def __init__(self):
        self.name = "garcia_2023_experiential_exp1"
        self.evals = [0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9]
        self.es_lotts = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        self.le_pairs = [(0.9,0.1),(0.8,0.2),(0.7,0.3),(0.6,0.4)]
        self.le_interleaved = False
        self.le_total = 120
        self.es_total = 96
        self.ee_total = 0
        self.ea_total = 0
        self.sa_total = 0
        self.sp_total = 12
        self.ee_evals = [0.1, 0.2, 0.3, 0.4, 0.6, 0.7, 0.8, 0.9]
        self.es_before_ee = False
        self.complete_feedback = False
        self.catch_p1 = [0.6, 0.7, 0.8, 0.9, 1.0]
        self.catch_p2 = [0.0, 0.1, 0.2, 0.3, 0.4]

    # ---- stimulus schedules ------------------------------------------------
    def _le_sched(self, rng):
        per = self.le_total // len(self.le_pairs)
        sched = [(hi, lo) for hi, lo in self.le_pairs for _ in range(per)]
        if self.le_interleaved:
            rng.shuffle(sched)
        else:
            rng.shuffle(sched)
            sched.sort(key=lambda ab: self.le_pairs.index((ab[0], ab[1])))
        return sched

    def _es_sched(self, n, rng):
        # ES trials beyond the full E x lottery crossing are catch trials: two
        # lotteries, one obviously better (Methods), drawn from the catch grids.
        n_catch = max(0, n - len(self.evals) * len(self.es_lotts))
        items = [(e, l, 0) for e in self.evals for l in self.es_lotts]
        out = []
        while len(out) < n - n_catch:
            rng.shuffle(items)
            for e, l, c in items:
                if len(out) >= n - n_catch:
                    break
                out.append((e, l, c))
        for _ in range(n_catch):
            out.append((float(rng.choice(self.catch_p1)), float(rng.choice(self.catch_p2)), 1))
        rng.shuffle(out)
        return out

    def _ee_sched(self, n, rng):
        items = [(i, j) for i in self.ee_evals for j in self.ee_evals if j != i]
        rng.shuffle(items)
        out = []
        while len(out) < n:
            for i, j in items:
                if len(out) >= n:
                    break
                out.append((i, j))
        return out

    def _hidden_sched(self, n, rng):
        out = []
        while len(out) < n:
            a = float(rng.choice(self.evals))
            b = float(rng.choice(self.evals))
            if a != b:
                out.append((a, b))
        return out

    def _sp_sched(self, n, rng):
        items = [("E", e) for e in self.evals] + [("S", l) for l in self.es_lotts]
        rng.shuffle(items)
        return [items[i % len(items)] for i in range(n)]

    # ---- full phase list ---------------------------------------------------
    def _phases(self, rng):
        phases = [("LE", self._le_sched(rng))]
        transfer = []
        if self.ee_total:
            transfer.append(("EE", self._ee_sched(self.ee_total, rng)))
        if self.es_total:
            transfer.append(("ES", self._es_sched(self.es_total, rng)))
        if self.es_before_ee:
            transfer.reverse()
        for ph, sched in transfer:
            phases.append((ph, sched))
        if self.ea_total:
            phases.append(("EA", self._hidden_sched(self.ea_total, rng)))
        if self.sa_total:
            phases.append(("SA", self._hidden_sched(self.sa_total, rng)))
        if self.sp_total:
            phases.append(("SP", self._sp_sched(self.sp_total, rng)))
        return phases

    # ---- simulation --------------------------------------------------------
    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            rng = np.random.default_rng(participant * 7919 + 13)
            pid = int(np.random.randint(10 ** 6, 10 ** 9))
            # symbol numbers: same seeding/permutation as build_jsonl._symbol_labels
            _vals = sorted(set(round(float(e), 2) for e in self.evals))
            labels = {v: 1 + int(k) for v, k in
                      zip(_vals, np.random.default_rng(pid % (2 ** 32)).permutation(len(_vals)))}
            prompt = WELCOME
            rew = 0.0
            prev_phase = None
            task_id = 0
            idx = 0
            for phase, sched in self._phases(rng):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                if prev_phase is not None:
                    prompt += "\n" + PHASE_GUIDE.get(phase, "")
                prev_phase = phase
                for trial, item in enumerate(sched):
                    if phase == "SP":
                        kind, p = item
                        d1 = _desc(kind, p, labels)
                        prompt += ("\nYou are shown one option: " + d1 +
                                   ". You report your estimate of its win probability (0 to 100): [HUMAN_RESPONSE]")
                        est = int(round(float(agent(prompt, choice_options=None))))
                        prompt += f"{est}[/HUMAN_RESPONSE]."
                        ok = abs(est / 100.0 - float(p)) <= 0.1
                        reward = 1.0 if ok else -1.0
                        rew += reward
                        rows.append(dict(participant_id=pid, task_id=task_id, trial=trial, phase=phase,
                                         response=float(est), reward=reward, condition=np.nan, correct=1.0 if ok else 0.0,
                                         sess=0.0, cfout=-1.0, chose_right=0.0, rew=rew, op1=kind, op2=np.nan,
                                         p1=float(p), p2=np.nan, ev1=_ev(p), ev2=np.nan, catch_trial=1.0 if kind == "S" else 0.0,
                                         reversed=0.0, index=idx))
                    else:
                        if phase == "ES":
                            op1, op2, p1, p2 = "E", "S", float(item[0]), float(item[1])
                        elif phase == "EA":
                            op1, op2, p1, p2 = "E", "A", float(item[0]), float(item[1])
                        elif phase == "SA":
                            op1, op2, p1, p2 = "S", "A", float(item[0]), float(item[1])
                        else:  # LE, EE
                            op1, op2, p1, p2 = "E", "E", float(item[0]), float(item[1])
                        cat = 1.0 if (phase == "ES" and item[2] == 1) else 0.0
                        d1 = _desc("S" if cat else op1, p1, labels)   # ES catch trial: two lotteries
                        d2 = _desc(op2, p2, labels)
                        rev = int(rng.random() < 0.5)
                        prompt += ("\nOption 1 (" + d1 + ") is on the " + ("right" if rev else "left") +
                                   "; option 2 (" + d2 + ") is on the " + ("left" if rev else "right") +
                                   ". You press [HUMAN_RESPONSE]")
                        token = agent(prompt, choice_options=["A", "B"])
                        response = 1 if token == "A" else 2
                        pc = p1 if response == 1 else p2
                        po = p2 if response == 1 else p1
                        reward = 1.0 if rng.random() < pc else -1.0
                        cfout = 1.0 if rng.random() < po else -1.0
                        ev_c = _ev(p1) if response == 1 else _ev(p2)
                        ev_o = _ev(p2) if response == 1 else _ev(p1)
                        correct = 1.0 if ev_c >= ev_o else 0.0
                        prompt += f"{token}[/HUMAN_RESPONSE]."
                        if phase == "LE":
                            prompt += _outcome(reward)
                            if self.complete_feedback:
                                prompt += _cf_outcome(cfout)
                        rew += reward
                        cond = self._cond(phase, p1, p2)
                        chose_right = 1.0 if (response == 1) == (rev == 0) else 0.0
                        rows.append({
                            "participant_id": pid, "task_id": task_id, "trial": trial, "phase": phase,
                            "response": float(response), "reward": float(reward), "condition": cond,
                            "correct": float(correct), "sess": 0.0, "cfout": float(cfout),
                            "chose_right": float(chose_right), "rew": rew, "op1": op1, "op2": op2,
                            "p1": float(p1), "p2": float(p2), "ev1": _ev(p1), "ev2": _ev(p2),
                            "catch_trial": float(cat), "reversed": float(rev), "index": idx,
                        })
                    idx += 1
                task_id += 1
            prompts.append(prompt)
        cols = ["participant_id", "task_id", "trial", "phase", "response", "reward",
                "condition", "correct", "sess", "cfout", "chose_right", "rew", "op1",
                "op2", "p1", "p2", "ev1", "ev2", "catch_trial", "reversed", "index"]
        df = pd.DataFrame(rows, columns=cols)
        return df, prompts

    def _cond(self, phase, p1, p2):
        if phase == "LE":
            for code, (hi, lo) in enumerate(self.le_pairs):
                if abs(float(p1) - hi) < 1e-9 and abs(float(p2) - lo) < 1e-9:
                    return float(code)
            return np.nan
        return np.nan


def _random_agent(prompt, choice_options):
    if choice_options is None:
        return 5 * int(np.random.randint(0, 21))
    return str(np.random.choice(choice_options))


def main():
    parser = argparse.ArgumentParser(description="Smoke-test this simulator with a uniform-random agent.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3)
    parser.add_argument("--max-chars", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()
    if args.seed is not None:
        np.random.seed(args.seed)
    task = GarciaExperiential()
    df, prompts = task.simulate(_random_agent, args.num_simulations, max_chars=args.max_chars)
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
            first = first[:90] + " ... " + first[-90:]
        print(f"participant {i} first line: {first}")
    print("=" * 78)
    print("first prompt, head:")
    print(prompts[0][:600])
    print("...")
    print("first prompt, tail:")
    print(prompts[0][-300:])


if __name__ == "__main__":
    main()
