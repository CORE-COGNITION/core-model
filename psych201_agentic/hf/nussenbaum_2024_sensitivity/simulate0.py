# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/nussenbaum_2024_sensitivity``
(Experiment 1: agency/bandit task + reward-sensitivity task + explicit-knowledge
task), format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py.
EXP0_MACHINE = {
    "bandit50a": "the yellow machine",
    "bandit50b": "the blue machine",
    "bandit70": "the green machine",
    "bandit30": "the red machine",
    "bandit90": "the purple machine",
    "bandit10": "the orange machine",
}
MACHINE_PROB = {
    "bandit50a": 0.5, "bandit50b": 0.5, "bandit70": 0.7,
    "bandit30": 0.3, "bandit90": 0.9, "bandit10": 0.1,
}
CONDITION_PAIR = {
    "bandits5050": ("bandit50a", "bandit50b"),
    "bandits7030": ("bandit70", "bandit30"),
    "bandits9010": ("bandit90", "bandit10"),
}

AGENCY_INSTR = (
    "Your goal is to win as many tokens as possible by playing slot machines that "
    "pay out 10 tokens with different probabilities. The tokens will be converted to "
    "a cash bonus at the end. Each trial you enter an arcade room holding two slot "
    "machines, and first the computer offers you some tokens to let it choose the "
    "machine for you. Press A to choose the machine for yourself, or press B to accept "
    "the offer and let the computer choose for you."
)
BANDIT_INSTR = (
    "If you chose to play for yourself, you then pick a machine: press A for the left "
    "machine, or press B for the right machine."
)
RS_INSTR = (
    "Now you will see pairs of slot machines, sometimes paired together that were not "
    "in the same room. Choose the slot machine that you think is most likely to give "
    "you tokens. If you are not sure, use your gut. You will not see whether you win "
    "or lose. Press A for the left machine, or press B for the right machine."
)
EXPLICIT_INSTR = (
    "Now you will see each slot machine one at a time and say what you think its chance "
    "of winning is. Use keys 1, 2, 3, 4, 5, 6, 7, 8, or 9 to answer, from 10% (1 out of every 10 trials) up to "
    "90% (9 out of every 10 trials)."
)
EXPERIMENT_HEADER = (
    "<Experiment 1> You win tokens by playing slot machines that pay out 10 tokens "
    "with different probabilities. Tokens convert to a cash bonus."
)


def _letter(resp, a_val, b_val):
    if pd.isna(resp):
        return None
    return "A" if resp == a_val else "B"


def _outcome(reward, tokens_earned, machine_label):
    parts = []
    if pd.notna(reward) and reward == 1:
        parts.append(f"{machine_label} pays out 10 tokens!")
    elif pd.notna(reward) and reward == 0:
        parts.append(f"{machine_label} pays out nothing.")
    if pd.notna(tokens_earned) and tokens_earned > 0:
        parts.append(f"You get {int(tokens_earned)} token{'s' if tokens_earned != 1 else ''}.")
    return " ".join(parts)


def _transcribe_exp0(g):
    """Exact mirror of build_jsonl.py transcribe_exp0 (per-participant df)."""
    g = g.sort_values(["task_id", "trial"]).reset_index(drop=True)
    lines = [EXPERIMENT_HEADER]

    t0 = g[g.task_id == 0].sort_values(["block", "trial"])
    if len(t0):
        lines.append("<Agency task>" + AGENCY_INSTR)
        lines.append("<Machine selection>" + BANDIT_INSTR)
        for block, b in t0.groupby("block"):
            agency_row = b[b.stage == "agency"]
            bandit_row = b[b.stage == "bandit"]
            if not len(agency_row) or not len(bandit_row):
                continue
            ar = agency_row.iloc[0]
            br = bandit_row.iloc[0]
            left = EXP0_MACHINE.get(ar["leftBandit"], ar["leftBandit"])
            right = EXP0_MACHINE.get(ar["rightBandit"], ar["rightBandit"])
            offer = ar["tokenOffer"]
            offer_txt = f"{int(offer)} token" if offer == 1 else f"{int(offer)} tokens"
            agency_resp = _letter(ar["agencyResp"], 2, 1)
            ag_free = pd.notna(ar["agencyResp"])
            chose_agency = (ar["agency"] == 1)
            bandit_resp = _letter(br["banditResp"], 1, 2)
            bandit_free = chose_agency and pd.notna(br["banditResp"])

            lines.append(
                f"You stand before the door to a room holding two slot machines: "
                f"{left} on the left and {right} on the right. The computer offers you "
                f"{offer_txt} to let it choose for you."
            )
            if ag_free:
                lines.append(f"You press [HUMAN_RESPONSE]{agency_resp}[/HUMAN_RESPONSE].")
            else:
                lines.append("You make no response.")
            sel = EXP0_MACHINE.get(br["selectedBandit"], br["selectedBandit"])
            if chose_agency:
                lines.append("You choose to play for yourself. You see the two machines.")
                if bandit_free:
                    lines.append(f"You press [HUMAN_RESPONSE]{bandit_resp}[/HUMAN_RESPONSE].")
                else:
                    lines.append("You make no response.")
            else:
                lines.append(
                    f"You accept the offer. A coin flip lands on {sel}, and you select it."
                )
            out = _outcome(br["reward"], br["tokensEarned"], sel)
            if out:
                lines.append(out)

    t1 = g[g.task_id == 1].sort_values("trial")
    if len(t1):
        lines.append("<Reward sensitivity task>" + RS_INSTR)
        for _, row in t1.iterrows():
            left = EXP0_MACHINE.get(row["leftBandit"], row["leftBandit"])
            right = EXP0_MACHINE.get(row["rightBandit"], row["rightBandit"])
            resp = _letter(row["banditKeyResp"], 1, 2)
            press = f"You press [HUMAN_RESPONSE]{resp}[/HUMAN_RESPONSE]." if resp is not None else "You make no response."
            lines.append(
                f"You see {left} on the left and {right} on the right. Which is more likely "
                f"to give you tokens? {press}"
            )

    t2 = g[g.task_id == 2].sort_values("trial")
    if len(t2):
        lines.append("<Explicit reward knowledge task>" + EXPLICIT_INSTR)
        for _, row in t2.iterrows():
            machine = EXP0_MACHINE.get(row["stimulus"], row["stimulus"])
            r = row["response"]
            resp = None if pd.isna(r) else str(int(r))
            press = f"You press [HUMAN_RESPONSE]{resp}[/HUMAN_RESPONSE]." if resp is not None else "You make no response."
            lines.append(
                f"You see {machine}. What is the chance of winning at this machine? "
                f"{press}"
            )
    return "\n".join(lines)


def _stage2_acc(condition, selected):
    if condition == "bandits5050":
        return None
    high = {"bandits7030": "bandit70", "bandits9010": "bandit90"}[condition]
    return 1.0 if selected == high else 0.0


class BanditAgencyTask:
    """Experiment 1 of Nussenbaum et al. (2024), "Sensitivity to the instrumental
    value of choice increases across development", Psychological Science, 35(8),
    933-947. Reproduces the full exp0 session.

    Design (Method > Experimental design > Agency task, p. 935): participants
    completed 315 two-stage bandit trials (15 blocks of 21; each block contains
    each of the 3 machine-pair conditions x the 7 token offers 0-6 once). Each
    trial begins with a free agency decision (A = choose agency / response 2,
    B = forgo / 1), then a machine selection that is free if agency was kept
    (A = left / 1, B = right / 2) or computer-selected by a coin flip if the
    participant forfeited. Machines pay 10 tokens with a fixed probability; a
    forfeit also pays the offer tokens. The six machines form 50/50, 70/30 and
    90/10 pairs. After the bandit task a reward-sensitivity task (pairs of
    machines, pick the more likely; A = left / 1, B = right / 2) and an
    explicit-knowledge task (rate each machine's win chance, keypad 1-9) follow.

    Token mapping is fixed (as in build_jsonl.py), not per-participant.

    ASSUMPTION: the paper does not fully specify the reward-sensitivity trial
    schedule, so this simulator uses the design measured in exp0.csv: all 30
    ordered pairs of distinct machines, each repeated 3 times (90 trials). Bandit
    left/right machine placement is randomized per trial; the machine pays out 10
    tokens with probability equal to its win probability. Rows are emitted in
    agency-then-bandit order within each block.

    The DataFrame matches exp0.csv minus the rt columns (rt, agencyRT, banditRT,
    RT) and the demographic columns (age, gender).
    """

    def __init__(self):
        self.name = "nussenbaum_2024_sensitivity_exp0"
        self.num_bandit_trials = 315
        self.num_rs_trials = 90
        self.offers = [0, 1, 2, 3, 4, 5, 6]

    def simulate(self, agent, num_simulations, max_chars=None):
        all_rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            rng = np.random.default_rng(np.random.randint(0, 2**31))
            pid = f"voc{participant + 1:03d}a"
            rows = []
            prompt = EXPERIMENT_HEADER
            prompt += "\n<Agency task>" + AGENCY_INSTR
            prompt += "\n<Machine selection>" + BANDIT_INSTR

            # ---- task 0: agency / bandit ----
            block = 0
            cond_count = {c: 0 for c in CONDITION_PAIR}
            for _ in range(15):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                combos = [(c, o) for c in CONDITION_PAIR for o in self.offers]
                rng.shuffle(combos)
                for condition, offer in combos:
                    cond_count[condition] += 1
                    trial_of_cond = cond_count[condition]
                    pid = f"voc{100 + participant:03d}a"
                    left_m, right_m = CONDITION_PAIR[condition]
                    if rng.random() < 0.5:
                        left_m, right_m = right_m, left_m
                    offer_txt = f"{offer} token" if offer == 1 else f"{offer} tokens"
                    prompt += (
                        f"\nYou stand before the door to a room holding two slot machines: "
                        f"{EXP0_MACHINE[left_m]} on the left and {EXP0_MACHINE[right_m]} on "
                        f"the right. The computer offers you {offer_txt} to let it choose for you."
                    )
                    prompt += "\nYou press [HUMAN_RESPONSE]"
                    agency_letter = agent(prompt, choice_options=["A", "B"])
                    prompt += f"{agency_letter}[/HUMAN_RESPONSE]."
                    agency_resp = 2 if agency_letter == "A" else 1
                    chose_agency = (agency_resp == 2)
                    if chose_agency:
                        prompt += "\nYou choose to play for yourself. You see the two machines."
                        prompt += "\nYou press [HUMAN_RESPONSE]"
                        bandit_letter = agent(prompt, choice_options=["A", "B"])
                        prompt += f"{bandit_letter}[/HUMAN_RESPONSE]."
                        bandit_resp = 1 if bandit_letter == "A" else 2
                        selected = left_m if bandit_resp == 1 else right_m
                        non_selected = right_m if bandit_resp == 1 else left_m
                    else:
                        side = int(rng.integers(1, 3))
                        bandit_resp = side
                        selected = left_m if side == 1 else right_m
                        non_selected = right_m if side == 1 else left_m
                        prompt += (
                            f"\nYou accept the offer. A coin flip lands on {EXP0_MACHINE[selected]}, "
                            f"and you select it."
                        )
                    reward = int(rng.random() < MACHINE_PROB[selected])
                    tokens_earned = reward + (offer if not chose_agency else 0)
                    out = _outcome(reward, tokens_earned, EXP0_MACHINE[selected])
                    if out:
                        prompt += "\n" + out
                    ev_choice = max(MACHINE_PROB[left_m], MACHINE_PROB[right_m]) * 10
                    ev_comp = 5 + offer
                    voc = round(ev_choice - ev_comp, 1)
                    for stage, response in (("agency", agency_resp - 1), ("bandit", 2 - bandit_resp)):
                        s2_acc = _stage2_acc(condition, selected) if stage == "bandit" else None
                        rows.append({
                            "participant_id": pid, "task_id": 0, "stage": stage,
                            "trial": block * 2 + (0 if stage == "agency" else 1),
                            "response": response, "block": block,
                            "condition": condition, "leftBandit": left_m, "rightBandit": right_m,
                            "tokenOffer": offer, "agencyResp": agency_resp,
                            "agency": 1 if chose_agency else 0,
                            "selectedBandit": selected, "nonSelectedBandit": non_selected,
                            "reward": reward if stage == "bandit" else None,
                            "tokensEarned": tokens_earned if stage == "bandit" else None,
                            "banditResp": bandit_resp if stage == "bandit" else None,
                            "stage_2_acc": s2_acc,
                            "ev_choice": ev_choice, "ev_comp": ev_comp, "voc": voc,
                            "trialOfCond": trial_of_cond,
                            "valid": 1,
                            "forced_choice": 1 if (stage == "bandit" and not chose_agency) else 0,
                        })
                    block += 1

            machines = list(MACHINE_PROB)

            # ---- task 1: reward sensitivity ----
            if max_chars is None or len(prompt) < max_chars:
                prompt += "\n<Reward sensitivity task>" + RS_INSTR
                pairs = [(l, r) for l in machines for r in machines if l != r]
                rng.shuffle(pairs)
                rs_pairs = (pairs * 3)[: self.num_rs_trials]
                for trial, (l_m, r_m) in enumerate(rs_pairs):
                    prompt += (
                        f"\nYou see {EXP0_MACHINE[l_m]} on the left and {EXP0_MACHINE[r_m]} on "
                        f"the right. Which is more likely to give you tokens? "
                        f"You press [HUMAN_RESPONSE]"
                    )
                    letter = agent(prompt, choice_options=["A", "B"])
                    prompt += f"{letter}[/HUMAN_RESPONSE]."
                    resp = 1 if letter == "A" else 2
                    diff = abs(MACHINE_PROB[l_m] - MACHINE_PROB[r_m])
                    if MACHINE_PROB[l_m] > MACHINE_PROB[r_m]:
                        correct, rs_acc = (1 if resp == 1 else 0), 1
                    elif MACHINE_PROB[l_m] < MACHINE_PROB[r_m]:
                        correct, rs_acc = (1 if resp == 2 else 0), -1
                    else:
                        correct, rs_acc = 0, 0
                    rows.append({
                        "participant_id": pid, "task_id": 1, "stage": None,
                        "trial": trial, "response": 2 - resp, "block": None,
                        "leftBandit": l_m, "rightBandit": r_m, "banditKeyResp": resp,
                        "diff": diff, "correct": correct, "rs_accuracy": rs_acc,
                        "valid": 1, "forced_choice": 0,
                    })

            # ---- task 2: explicit ----
            if max_chars is None or len(prompt) < max_chars:
                prompt += "\n<Explicit reward knowledge task>" + EXPLICIT_INSTR
                for trial, m in enumerate(machines):
                    prompt += (
                        f"\nYou see {EXP0_MACHINE[m]}. What is the chance of winning at this "
                        f"machine? You press [HUMAN_RESPONSE]"
                    )
                    resp = int(agent(prompt, choice_options=[str(i) for i in range(1, 10)]))
                    prompt += f"{resp}[/HUMAN_RESPONSE]."
                    rows.append({
                        "participant_id": pid, "task_id": 2, "stage": None,
                        "trial": trial, "response": resp, "block": None,
                        "stimulus": m, "bandit": m, "trueProb": MACHINE_PROB[m],
                        "error": abs(resp - MACHINE_PROB[m]), "valid": 1, "forced_choice": 0,
                    })

            all_rows.extend(rows)
            prompts.append(prompt)
        df = pd.DataFrame(all_rows)
        if "response" in df.columns:
            df["response"] = df["response"].astype("float64")
        return df, prompts


def _random_agent(prompt, choice_options):
    return str(np.random.choice(choice_options))


def main():
    parser = argparse.ArgumentParser(description="Smoke-test this simulator with a uniform-random agent.")
    parser.add_argument("-n", "--num-simulations", type=int, default=3, help="number of simulated participants (default: 3)")
    parser.add_argument("--max-chars", type=int, default=None, help="stop each participant at the block boundary at/past this many chars")
    parser.add_argument("--seed", type=int, default=None, help="numpy random seed")
    args = parser.parse_args()
    if args.seed is not None:
        np.random.seed(args.seed)
    task = BanditAgencyTask()
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