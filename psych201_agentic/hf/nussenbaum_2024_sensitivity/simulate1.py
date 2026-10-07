# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp1 of ``Hugging-Brain/nussenbaum_2024_sensitivity``
(Experiment 2: arcade/agency task + explicit-knowledge task), format-identical
to the repo's ``transcripts1.jsonl``.

``uv run simulate1.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

HEX_COLOR = {
    "#FA92F8": "pink", "#1CD855": "green", "#3386FF": "blue",
    "#741CD8": "purple", "#D8271C": "red", "#D89F1C": "orange",
}
COLORS = ["#FA92F8", "#1CD855", "#3386FF", "#741CD8", "#D8271C", "#D89F1C"]
# machine id -> win probability (fixed across participants, Experiment 2)
ID_PROB = {0: 0.9, 1: 0.1, 2: 0.7, 3: 0.3, 4: 0.5, 5: 0.5}
# arcade context -> the two machine ids in that room
CONTEXT_IDS = {0: (1, 0), 1: (2, 3), 2: (4, 5)}

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
EXPLICIT_INSTR = (
    "Now you will see each slot machine one at a time and say what you think its chance "
    "of winning is. Use keys 1, 2, 3, 4, 5, 6, 7, 8, or 9 to answer, from 10% (1 out of every 10 trials) up to "
    "90% (9 out of every 10 trials)."
)
EXPERIMENT_HEADER = (
    "<Experiment 2> You win tokens by playing slot machines that pay out 10 tokens "
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


def _color(hexv):
    return HEX_COLOR.get(hexv, hexv)


def _transcribe_exp1(g):
    """Exact mirror of build_jsonl.py transcribe_exp1 (single participant group)."""
    g = g.sort_values(["task_id", "trial"]).reset_index(drop=True)
    lines = [EXPERIMENT_HEADER]

    t0 = g[g.task_id == 0].sort_values(["block", "trial"])
    if len(t0):
        lines.append("<Arcade task>" + AGENCY_INSTR)
        lines.append("<Machine selection>" + BANDIT_INSTR)
        for block, b in t0.groupby("block"):
            agency_row = b[b.stage == "agency"]
            bandit_row = b[b.stage == "bandit"]
            if not len(agency_row) or not len(bandit_row):
                continue
            ar = agency_row.iloc[0]
            br = bandit_row.iloc[0]
            left = _color(ar["arcade_color_L"])
            right = _color(ar["arcade_color_R"])
            offer = ar["offer"]
            offer_txt = f"{int(offer)} token" if offer == 1 else f"{int(offer)} tokens"
            agency_resp = _letter(ar["stage_1_choice"], 1, 0)
            ag_free = pd.notna(ar["stage_1_choice"])
            chose_agency = (ar["stage_1_choice"] == 1)
            bandit_resp = _letter(br["stage_2_choice"], 1, 0)
            bandit_free = chose_agency and pd.notna(br["stage_2_choice"])

            lines.append(
                f"You enter an arcade room holding two slot machines: the {left} machine "
                f"on the left and the {right} machine on the right. The computer offers you "
                f"{offer_txt} to let it choose for you."
            )
            if ag_free:
                lines.append(f"You press [HUMAN_RESPONSE]{agency_resp}[/HUMAN_RESPONSE].")
            else:
                lines.append("You make no response.")
            if chose_agency:
                lines.append("You choose to play for yourself. You see the two machines.")
                if bandit_free:
                    lines.append(f"You press [HUMAN_RESPONSE]{bandit_resp}[/HUMAN_RESPONSE].")
                else:
                    lines.append("You make no response.")
                sel = left if (pd.notna(br["stage_2_choice"]) and br["stage_2_choice"] == 1) else right
            else:
                sel_side = br["stage_2_choice"]
                sel = left if (pd.notna(sel_side) and sel_side == 1) else right
                lines.append(
                    f"You accept the offer. A coin flip lands on the {sel} machine, "
                    f"and you select it."
                )
            tokens_earned = br["reward"]
            if pd.notna(tokens_earned) and not chose_agency and pd.notna(ar["offer"]):
                tokens_earned = tokens_earned + ar["offer"]
            out = _outcome(br["reward"], tokens_earned, f"The {sel} machine")
            if out:
                lines.append(out)

    t1 = g[g.task_id == 1].sort_values("trial")
    if len(t1):
        lines.append("<Explicit reward knowledge task>" + EXPLICIT_INSTR)
        colors = ["red", "blue", "orange", "green", "pink", "purple"]
        machine_color = {}
        used = set()
        for _, row in t1.iterrows():
            cands = [c for c in colors if c not in used
                     and pd.notna(row[c]) and abs(row[c] - row["true_prob"]) < 1e-9]
            chosen = cands[0] if cands else None
            machine_color[row["stimulus"]] = chosen
            if chosen:
                used.add(chosen)
        for _, row in t1.iterrows():
            mc = machine_color[row["stimulus"]]
            machine = f"the {mc} machine" if mc else "a slot machine"
            r = row["response"]
            resp = None if pd.isna(r) else str(int(r))
            press = f"You press [HUMAN_RESPONSE]{resp}[/HUMAN_RESPONSE]." if resp is not None else "You make no response."
            lines.append(
                f"You see {machine}. What is the chance of winning at this machine? "
                f"{press}"
            )
    return "\n".join(lines)


class ArcadeAgencyTask:
    """Experiment 2 of Nussenbaum et al. (2024), "Sensitivity to the instrumental
    value of choice increases across development", Psychological Science, 35(8),
    933-947. Reproduces the full exp1 session.

    Design (Method > Experimental design > Agency task, p. 935, plus SI; the
    Experiment 2 task statistics are identical to Experiment 1, see the
    "Preregistered replication" method, p. 938): participants completed 315
    two-stage arcade trials (each of 3 arcade-room machine pairs x the 7 token
    offers 0-6, order randomized). Each trial begins with a free agency decision
    (A = choose agency / stage_1_choice 1, B = forgo / 0), then a machine
    selection that is free if agency was kept (A = left / 1, B = right / 0) or
    computer-selected by a coin flip if the participant forfeited. Machines pay
    10 tokens with a fixed probability; a forfeit also pays the offer tokens.
    The six machines have fixed win probabilities (0.9, 0.1, 0.7, 0.3, 0.5, 0.5)
    and are paired into three contexts. After the arcade task an
    explicit-knowledge task (rate each machine's win chance, keypad 1-9) follows.

    Each participant receives a random assignment of the six arcade colours to
    the six machine probabilities (as in the real data), so the colour a reader
    must learn is randomized per participant. Token mapping follows
    build_jsonl.py (fixed): agency A = 1 / B = 0; machine A = left / 1,
    B = right / 0.

    ASSUMPTION: the paper does not fully specify the per-trial machine-pair /
    offer schedule, so it uses the design measured in exp1.csv: 315 trials over
    3 contexts x 7 offers, with the left/right machine placement randomized per
    trial and the machine paying out 10 tokens with probability equal to its win
    probability. arcade_block is assigned as block//45 + 1 (45 trials per block,
    7 blocks).

    The DataFrame matches exp1.csv minus the rt columns (rt, stage_1_rt,
    stage_2_rt) and the demographic columns (age, gender).
    """

    def __init__(self):
        self.name = "nussenbaum_2024_sensitivity_exp1"
        self.num_arcade_trials = 315
        self.offers = [0, 1, 2, 3, 4, 5, 6]

    def simulate(self, agent, num_simulations, max_chars=None):
        all_rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            rng = np.random.default_rng(np.random.randint(0, 2**31))
            rows = []
            prompt = EXPERIMENT_HEADER
            prompt += "\n<Arcade task>" + AGENCY_INSTR
            prompt += "\n<Machine selection>" + BANDIT_INSTR

            # random assignment of colours to machine ids for this participant
            color_of_id = dict(zip(sorted(ID_PROB), rng.permutation(COLORS)))

            block = 0
            for _ in range(15):
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                combos = [(c, o) for c in CONTEXT_IDS for o in self.offers]
                rng.shuffle(combos)
                for context, offer in combos:
                    id_l, id_r = CONTEXT_IDS[context]
                    if rng.random() < 0.5:
                        id_l, id_r = id_r, id_l
                    color_l, color_r = color_of_id[id_l], color_of_id[id_r]
                    prob_l, prob_r = ID_PROB[id_l], ID_PROB[id_r]
                    offer_txt = f"{offer} token" if offer == 1 else f"{offer} tokens"
                    prompt += (
                        f"\nYou enter an arcade room holding two slot machines: the "
                        f"{_color(color_l)} machine on the left and the {_color(color_r)} "
                        f"machine on the right. The computer offers you {offer_txt} to let "
                        f"it choose for you."
                    )
                    prompt += "\nYou press [HUMAN_RESPONSE]"
                    agency_letter = agent(prompt, choice_options=["A", "B"])
                    prompt += f"{agency_letter}[/HUMAN_RESPONSE]."
                    stage1 = 1 if agency_letter == "A" else 0
                    chose_agency = (stage1 == 1)
                    if chose_agency:
                        prompt += "\nYou choose to play for yourself. You see the two machines."
                        prompt += "\nYou press [HUMAN_RESPONSE]"
                        bandit_letter = agent(prompt, choice_options=["A", "B"])
                        prompt += f"{bandit_letter}[/HUMAN_RESPONSE]."
                        stage2 = 1 if bandit_letter == "A" else 0
                        sel_id = id_l if stage2 == 1 else id_r
                    else:
                        stage2 = int(rng.integers(0, 2))
                        sel_id = id_l if stage2 == 1 else id_r
                        sel_color = color_of_id[sel_id]
                        prompt += (
                            f"\nYou accept the offer. A coin flip lands on the {_color(sel_color)} "
                            f"machine, and you select it."
                        )
                    sel_color = color_of_id[sel_id]
                    outcome = 10 if rng.random() < ID_PROB[sel_id] else 0
                    for stage, stage_col, resp, sel in (("agency", "stage_1_choice", stage1, None),
                                                        ("bandit", "stage_2_choice", stage2, sel_id)):
                        reward_val = outcome if stage == "bandit" else None
                        tokens_earned = (outcome + (offer if not chose_agency else 0)) if stage == "bandit" else None
                        prompt_out = _outcome(reward_val, tokens_earned, f"The {_color(color_of_id[sel])} machine") if stage == "bandit" else ""
                        if stage == "bandit" and prompt_out:
                            prompt += "\n" + prompt_out
                        rows.append({
                            "participant_id": participant, "task_id": 0, "stage": stage,
                            "trial": block * 2 + (0 if stage == "agency" else 1),
                            "response": resp, "block": block,
                            "arcade_block": block // 45 + 1, "context": context, "offer": offer,
                            "arcade_color_L": color_l, "arcade_color_R": color_r,
                            "arcade_id_L": id_l, "arcade_id_R": id_r,
                            "reward_prob_L": prob_l, "reward_prob_R": prob_r,
                            "stage_1_choice": stage1, "stage_2_choice": stage2,
                            "reward": reward_val, "stage_3_outcome": reward_val,
                            "phase": "experiment", "valid": 1,
                            "forced_choice": 1 if (stage == "bandit" and not chose_agency) else 0,
                        })
                    block += 1

            # ---- explicit task ----
            if max_chars is None or len(prompt) < max_chars:
                prompt += "\n<Explicit reward knowledge task>" + EXPLICIT_INSTR
                # assign each machine a colour and a true_prob (as in the real data
                # the colour->prob map is constant across a participant's six rows)
                probs = [0.1, 0.3, 0.5, 0.5, 0.7, 0.9]
                rng.shuffle(probs)
                color_names = ["red", "blue", "orange", "green", "pink", "purple"]
                color_prob = dict(zip(color_names, probs))
                # each machine shows a distinct colour whose prob is its true_prob
                machine_order = list(color_names)
                rng.shuffle(machine_order)
                exp_rows = []
                for trial, color_name in enumerate(machine_order):
                    stimulus = f"static/img/machines/machine{trial + 1}.png"
                    exp_rows.append({
                        "stimulus": stimulus, "true_prob": color_prob[color_name],
                        "trial": trial,
                    })
                # replicate build_jsonl.py machine_color logic to pick narrated colour
                machine_color = {}
                used = set()
                for row in exp_rows:
                    cands = [c for c in color_names if c not in used
                             and abs(color_prob[c] - row["true_prob"]) < 1e-9]
                    chosen = cands[0] if cands else None
                    machine_color[row["stimulus"]] = chosen
                    if chosen:
                        used.add(chosen)
                for row in exp_rows:
                    prompt += (
                        f"\nYou see the {machine_color[row['stimulus']]} machine. What is the "
                        f"chance of winning at this machine? You press [HUMAN_RESPONSE]"
                    )
                    resp = int(agent(prompt, choice_options=[str(i) for i in range(1, 10)]))
                    prompt += f"{resp}[/HUMAN_RESPONSE]."
                    rows.append({
                        "participant_id": participant, "task_id": 1, "stage": None,
                        "trial": row["trial"], "response": resp, "block": None,
                        "stimulus": row["stimulus"], "true_prob": row["true_prob"],
                        "error": abs(resp - row["true_prob"]),
                        "phase": "explicit", "valid": 1, "forced_choice": 0,
                        "red": color_prob["red"], "blue": color_prob["blue"],
                        "orange": color_prob["orange"], "green": color_prob["green"],
                        "pink": color_prob["pink"], "purple": color_prob["purple"],
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
    task = ArcadeAgencyTask()
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