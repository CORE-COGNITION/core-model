# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/witte_2024_how``, format-identical
to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.

One simulation = one participant. The repo's bandit reward sets were
pre-sampled once and are identical for every participant (paper Methods,
"General procedure": "The stimulus sets ... rewards in the bandit tasks were
pre-sampled and the same for all participants"); the simulator mirrors this by
drawing one reward set per session and reusing it for every participant. Only
the agent's choices and the demographics / WM / questionnaire / feedback draws
differ between simulated participants.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# --- Verbatim narration from build_jsonl.py -----------------------------------
NA = float("nan")
ARM2 = ["S", "K"]
ARM4 = ["S", "D", "K", "L"]

WM_MEASURES = {
    "OS_recall": ("operation-span", "recall accuracy"),
    "SS_recall": ("symmetry-span", "recall accuracy"),
    "WMU_recall": ("updating", "recall accuracy"),
    "OS_processing": ("operation-span", "processing accuracy"),
    "SS_processing": ("symmetry-span", "processing accuracy"),
    "prop_timeout_os_processing": ("operation-span", "proportion of timed-out processing responses"),
    "prop_timeout_ss_processing": ("symmetry-span", "proportion of timed-out processing responses"),
    "rt_os": ("operation-span", "mean processing reaction time"),
    "rt_ss": ("symmetry-span", "mean processing reaction time"),
}
WM_ORDER = list(WM_MEASURES)

COND_LABEL = {"SS": "both arms stable", "SF": "arm 1 stable, arm 2 drifting",
              "FS": "arm 1 drifting, arm 2 stable", "FF": "both arms drifting"}

SCALE_ANCHORS = {
    "PANAS": "0 = very slightly or not at all, 1 = a little, 2 = moderately, 3 = quite a bit, 4 = extremely",
    "STICSA": "0 = almost never, 1 = occasionally, 2 = often, 3 = almost always",
    "BIG_5": "0 = disagree strongly, 1 = disagree a little, 2 = neutral, 3 = agree a little, 4 = agree strongly",
    "PHQ_9": "0 = not at all, 1 = several days, 2 = more than half the days, 3 = nearly every day",
    "CEI": "0 = strongly disagree, 1 = disagree, 2 = somewhat disagree, 3 = neither, "
           "4 = somewhat agree, 5 = agree, 6 = strongly agree",
}
QQ_ORDER = ["PANAS", "STICSA", "BIG_5", "PHQ_9", "CEI"]
QQ_NITEMS = {"PANAS": 20, "STICSA": 22, "BIG_5": 6, "PHQ_9": 10, "CEI": 4}
QQ_MAX = {"PANAS": 4, "STICSA": 3, "BIG_5": 4, "PHQ_9": 3, "CEI": 6}

WM_INSTRUCTION = (
    "In the memory phase you complete three working-memory tasks in a row: an operation-span "
    "task, a symmetry-span task, and an updating task. In each you recall items while doing a "
    "concurrent processing task. The scores below are your recorded results for the phase."
)
HORIZON_INSTRUCTION = (
    "In this task you play many rounds with two slot machines: left = S, right = K. A message "
    "above the machines tells you whether this is a long round (10 picks) or a short round "
    "(5 picks). In the first four picks of every round one machine is highlighted and you must "
    "press that machine's key; after that you choose freely. After every pick you see the points "
    "that machine paid out."
)
TWOARM_INSTRUCTION = (
    "In this task you play 30 rounds of 10 free choices between the same two slot machines: "
    "left (S) and right (K). Within a round the machines pay points that may stay stable or "
    "drift; after each choice you see the points the chosen machine paid."
)
FOURARM_INSTRUCTION = (
    "In this task you play one long round of 200 free choices between four slot machines, "
    "played with S, D, K and L. After each choice you see the points the chosen machine paid "
    "out; the machines' average payouts drift slowly."
)
QUESTIONNAIRE_INSTRUCTION = (
    "Finally you complete five questionnaires. For each item you are given a statement or a "
    "word and answer with a single number on the stated scale. Answer each item with exactly "
    "that number."
)

# Per-participant demographic / meta draws (empirical distributions from exp0.csv).
EDU_POOL = (["4", "8", "10", "11"] * 6 + ["12"] * 22 + ["13"] * 13 + ["14"] * 18
            + ["15"] * 20 + ["16"] * 54 + ["17"] * 32 + ["18"] * 22 + ["19"] * 8
            + ["20"] * 8 + ["21"] * 7 + ["22"] * 4 + ["23"] + ["24"] * 5 + ["25"] * 2)
TEXT_EDU_POOL = ["college", "highschool", "University", "16 years", "uni",
                 "8 years primary, 6 years highschool, first year university"]
FEEDBACK_POOL = [
    "The last slot machine game felt too long.",
    "Interesting study, good luck!",
    "The tasks were quite challenging but fun.",
    "No further feedback.",
    "The working-memory tasks were the hardest part.",
    "Very engaging experiment.",
    "",
]


def num(v):
    v = v.item() if hasattr(v, "item") else v
    if pd.isna(v):
        return "?"
    f = float(v)
    return str(int(f)) if f.is_integer() else f"{f:g}"


class ExplorationBattery:
    """Full two-session battery of Witte, Thalmann & Schulz (2024), "How should
    we measure exploration?" (PsyArXiv preprint, doi:10.31234/osf.io/tzuey).

    Design (Methods, "Bandit tasks"): three bandit tasks after the WM tasks and
    before the questionnaires in each of two sessions.
      - Horizon task (p. 6-7): 1 practice round + 80 task rounds of 4 forced
        + 1 (short) / 6 (long) free choices between two machines; the reward
        set fully crossed horizon length (5/10) and information condition
        (-1/0/1) so every condition averaged the same reward difference, drawn
        from {30, 20, 12, 8, 4}. Per-game arm means keep both arms equally
        rewarding overall; payouts are rounded Gaussian noise around each arm's
        mean, clipped to 0-100.
      - Two-armed bandit (p. 7; after Fan et al. 2010 / Gershman 2018): 30
        rounds x 10 free choices under SS/SF/FS/FF reward conditions; stable
        arms pay Gaussian noise around a fixed mean, drifting arms around a
        Gaussian random walk.
      - Restless bandit (p. 7-8; Daw et al. 2006): 200 free choices among four
        arms whose means follow mu_{t+1} = lambda*mu_t + (1-lambda)*50 + v,
        lambda = .9836, v ~ N(0, 2.8); observed payouts are rounded Gaussian
        noise around the current mean, clipped to 0-100.
    Questionnaires (p. 8): PANAS, STICSA, BIG_5, PHQ_9, CEI with the stated
    Likert scales. WM session scores (operation span, symmetry span, updating)
    are narrated as recorded results.

    ASSUMPTION: the OSF pre-sampled reward sets are not shipped, so this
    simulator draws fresh sets from the paper's generative processes
    (differences {30,20,12,8,4} for Horizon; sd_v ~ 4 random-walk steps for the
    two-armed drift; Daw et al. lambda equation for the restless arms). Horizon
    per-game means are drawn with the better-arm sign random and arm 1 in
    ~[38,64] to reproduce the observed shape; the exact OSF draw order is not
    recoverable.

    ASSUMPTION: session2 is present with p = 177/238 and the WM block with
    p = 354/413, matching exp0.csv. Questionnaires always present.

    ASSUMPTION: demographics (gender, age, edu, income band, motivations,
    feedback) are sampled from exp0.csv's empirical distributions; age is drawn
    from N(34.2, 7.8) clipped to 18-66 (the source contains one erroneous
    extreme age of ~43M that is not reproduced). The last participant of every
    run is forced a free-text edu (mirroring the real CSV, whose edu column
    carries occasional free-text values) so that pandas keeps the column object
    and numeric codes print without a trailing ".0".

    The DataFrame matches exp0.csv minus ``rt`` and ``questionnaire_duration``.
    """

    def __init__(self):
        self.name = "witte_2024_how_exp0"
        self.num_games_horizon = 80
        self.num_games_twoarm = 30
        self.num_trials_restless = 200
        self._reward_sets = {}      # session -> {"horizon_meta", "horizon_rew",
                                    #             "twoarm_cond", "twoarm_rew", "restless_rew"}

    # ------------------------------------------------------------------ design
    def _horizon_set(self, session):
        meta = []
        for h in (10, 5):
            for info, n in ((0, 20), (1, 10), (-1, 10)):
                for _ in range(n):
                    meta.append([h, info, [1 if np.random.rand() < 0.5 else 0 for _ in range(4)]])
        np.random.shuffle(meta)
        rew = []
        for h, info, forced in meta:
            d = int(np.random.choice([4, 8, 12, 20, 30]))
            sign = 1 if np.random.rand() < 0.5 else -1
            m1 = np.random.randint(38, 65)
            m2 = int(np.clip(m1 + sign * d, 0, 100))
            block = []
            for _ in range(10):
                r1 = int(np.clip(round(np.random.normal(m1, 4.0)), 0, 100))
                r2 = int(np.clip(round(np.random.normal(m2, 4.0)), 0, 100))
                block.append([r1, r2])
            rew.append(block)
        return meta, rew

    def _twoarm_set(self, session):
        conds = ["SS"] * 10 + ["FF"] * 10 + ["FS"] * 6 + ["SF"] * 4
        np.random.shuffle(conds)
        rew = []
        for cond in conds:
            arm1_drift = cond in ("FF", "FS")
            arm2_drift = cond in ("FF", "SF")
            m1 = float(np.random.randint(10, 91))
            m2 = float(np.random.randint(10, 91))
            block = []
            for _ in range(10):
                r1 = int(np.clip(round(np.random.normal(m1, 1.0)), 0, 100))
                r2 = int(np.clip(round(np.random.normal(m2, 1.0)), 0, 100))
                block.append([r1, r2])
                if arm1_drift:
                    m1 = float(np.clip(m1 + np.random.normal(0.0, 4.0), 0, 100))
                if arm2_drift:
                    m2 = float(np.clip(m2 + np.random.normal(0.0, 4.0), 0, 100))
            rew.append(block)
        return conds, rew

    def _restless_set(self, session):
        mu = np.clip(50.0 + np.random.normal(0.0, 5.0, 4), 0, 100)
        rew = np.zeros((200, 4), dtype=int)
        for t in range(200):
            rew[t] = np.clip(np.round(np.random.normal(mu, 4.0)), 0, 100)
            mu = np.clip(0.9836 * mu + (1.0 - 0.9836) * 50.0 + np.random.normal(0.0, 2.8, 4), 0, 100)
        return [row.tolist() for row in rew]

    def _reward_set(self, session):
        if session not in self._reward_sets:
            hm, hr = self._horizon_set(session)
            tc, tr = self._twoarm_set(session)
            rr = self._restless_set(session)
            self._reward_sets[session] = {
                "horizon_meta": hm, "horizon_rew": hr,
                "twoarm_cond": tc, "twoarm_rew": tr, "restless_rew": rr,
            }
        return self._reward_sets[session]

    # ------------------------------------------------------------------ draws
    def _draw_demographics(self):
        gender = str(np.random.choice(["m", "f", "other"], p=[0.499, 0.494, 0.007]))
        age = int(np.clip(round(np.random.normal(34.2, 7.8)), 18, 66))
        edu = str(np.random.choice(EDU_POOL))
        income_0 = int(np.random.randint(0, 9))
        motiv_mem_0 = int(np.clip(round(np.random.normal(91.0, 13.0)), 0, 100))
        motiv_slot_0 = int(np.clip(round(np.random.normal(85.0, 21.0)), 0, 100))
        mem_aid_0, slot_aid_0, attention1 = 0, 0, 2.0
        feedback = str(np.random.choice(FEEDBACK_POOL))
        return dict(gender=gender, age=age, edu=edu, income_0=income_0,
                    motiv_mem_0=motiv_mem_0, motiv_slot_0=motiv_slot_0,
                    mem_aid_0=mem_aid_0, slot_aid_0=slot_aid_0,
                    attention1=attention1, feedback=feedback)

    def _draw_wm(self):
        def prop(lo, hi):
            return round(np.random.uniform(lo, hi), 6)
        return {
            "OS_recall": prop(0.55, 0.95), "SS_recall": prop(0.48, 0.95),
            "WMU_recall": prop(0.50, 0.92), "OS_processing": prop(0.89, 1.0),
            "SS_processing": prop(0.93, 1.0),
            "prop_timeout_os_processing": round(np.random.uniform(0.0, 0.012), 6),
            "prop_timeout_ss_processing": round(np.random.uniform(0.0, 0.004), 6),
            "rt_os": round(np.random.uniform(5200, 15000), 3),
            "rt_ss": round(np.random.uniform(2400, 9000), 3),
        }

    def _qq_stem(self, q):
        if q == "PANAS":
            return "PANAS: for each of the 20 words below, rate how well it describes how you feel right now"
        if q == "STICSA":
            return "STICSA: for each of the 22 statements below, rate how often it is generally true for you"
        if q == "BIG_5":
            return "BIG_5 openness: for each of the 6 statements below, rate your agreement"
        if q == "PHQ_9":
            return "PHQ_9: for each of the 10 items below, rate how often you have been bothered by it over the last two weeks"
        return "CEI: for each of the 4 statements below, rate your agreement"

    # -------------------------------------------------------------- simulate
    def simulate(self, agent, num_simulations, max_chars=None):
        all_rows = []
        prompts = []
        for participant in tqdm(range(num_simulations)):
            demo = self._draw_demographics()
            if participant == num_simulations - 1:
                # Guarantee the edu column keeps some free-text value (as the
                # real exp0.csv does), so pandas reads edu back as object and
                # numeric codes print without a trailing ".0".
                demo["edu"] = str(np.random.choice(TEXT_EDU_POOL))
            rows = []
            trial = {}          # task_id -> next trial index
            prompt = ""

            def add_line(s):
                nonlocal prompt
                prompt += (s if not prompt else "\n" + s)

            def start_trial():
                nonlocal prompt
                prompt += "\n"

            def append_tok(s):
                nonlocal prompt
                prompt += s

            def base_row(sess, task_id):
                key = task_id
                t = trial.get(key, 0)
                trial[key] = t + 1
                return {
                    "participant_id": participant, "trial": t, "response": NA,
                    "task_id": task_id, "session": sess, "phase": None, "block": NA,
                    "reward": NA, "info": NA, "reward1": NA, "reward2": NA,
                    "horizon": NA, "forced_choice": NA, "valid": 1,
                    "condition": None, "reward3": NA, "reward4": NA,
                    "questionnaire": None, "item_index": NA, "motiv_mem_0": NA,
                    "motiv_slot_0": NA, "mem_aid_0": NA, "slot_aid_0": NA,
                    "gender": None, "feedback": None, "age": NA, "edu": None,
                    "income_0": NA, "attention1": NA, "wm_measure": None,
                }

            def horizon_row(sess, block, t, forced, valid, rw, resp):
                r = base_row(sess, 0)
                r.update(block=float(block), reward=float(rw[resp]) if resp is not None else NA,
                         info=float(meta[b][1]), reward1=float(rw[0]), reward2=float(rw[1]),
                         horizon=float(meta[b][0]), forced_choice=forced, valid=int(valid),
                         response=float(resp) if resp is not None else NA)
                return r

            def twoarm_row(sess, block, t, cond, rw, resp):
                r = base_row(sess, 1)
                r.update(block=float(block), reward=float(rw[resp]),
                         reward1=float(rw[0]), reward2=float(rw[1]),
                         forced_choice=0.0, condition=cond, response=float(resp))
                return r

            def restless_row(sess, t, rw, resp):
                r = base_row(sess, 2)
                r.update(reward=float(rw[resp]), reward1=float(rw[0]), reward2=float(rw[1]),
                         reward3=float(rw[2]), reward4=float(rw[3]),
                         forced_choice=0.0, response=float(resp))
                return r

            def qq_row(sess, q, i, resp):
                r = base_row(sess, 4)
                r.update(phase="questionnaire", reward=NA, forced_choice=NA,
                         questionnaire=q, item_index=float(i), response=float(resp),
                         motiv_mem_0=float(demo["motiv_mem_0"]),
                         motiv_slot_0=float(demo["motiv_slot_0"]),
                         mem_aid_0=float(demo["mem_aid_0"]),
                         slot_aid_0=float(demo["slot_aid_0"]),
                         gender=demo["gender"], feedback=demo["feedback"],
                         age=float(demo["age"]), edu=demo["edu"],
                         income_0=float(demo["income_0"]), attention1=demo["attention1"])
                return r

            add_line("You take part in a two-session study on decision-making and memory.")
            add_line(f"You are {demo['gender']}, age {num(demo['age'])}, "
                     f"education code {demo['edu']}, income band {num(demo['income_0'])}.")

            sessions = ["session1"]
            if np.random.rand() < 177 / 238.0:
                sessions.append("session2")

            for sess in sessions:
                if max_chars is not None and len(prompt) >= max_chars:
                    break
                add_line(f"Session {sess}")

                if np.random.rand() < 354 / 413.0:
                    wm_vals = self._draw_wm()
                    add_line(WM_INSTRUCTION)
                    for measure in WM_ORDER:
                        task, what = WM_MEASURES[measure]
                        v = wm_vals[measure]
                        if measure.startswith("rt_"):
                            add_line(f"Your {what} on the {task} task was {num(v)} ms.")
                        else:
                            add_line(f"Your {what} on the {task} task was {num(v)}.")
                        r = base_row(sess, 3)
                        r.update(phase="working_memory", response=float(v), wm_measure=measure)
                        rows.append(r)

                if max_chars is not None and len(prompt) >= max_chars:
                    break
                add_line("You now play the Horizon task.")
                add_line(HORIZON_INSTRUCTION)
                rs = self._reward_set(sess)
                meta, rew = rs["horizon_meta"], rs["horizon_rew"]
                for b in range(self.num_games_horizon):
                    if max_chars is not None and len(prompt) >= max_chars:
                        break
                    h, info, forced = meta[b]
                    kind = "long" if h == 10 else "short"
                    add_line(f"Round {b + 1}: {kind}, information condition {info}.")
                    for t in range(4):
                        a = ARM2[forced[t]]
                        add_line(f"The {a} machine is highlighted, so you press {a}. "
                                 f"You win {num(rew[b][t][forced[t]])} points.")
                        rows.append(horizon_row(sess, b, t, 1.0, 1, rew[b][t], forced[t]))
                    add_line("The machines disappear, reminding you how many free choices remain.")
                    if h == 10:
                        add_line("You are told you can make six free choices.")
                        nfree = 6
                    else:
                        add_line("You are told you can make one free choice.")
                        nfree = 1
                    for t in range(4, 4 + nfree):
                        start_trial()
                        append_tok("You press [HUMAN_RESPONSE]")
                        choice = agent(prompt, choice_options=["S", "K"])
                        resp = ARM2.index(choice)
                        append_tok(f"{choice}[/HUMAN_RESPONSE]. You win {num(rew[b][t][resp])} points.")
                        rows.append(horizon_row(sess, b, t, 0.0, 1, rew[b][t], resp))
                    if h == 5:
                        for t in range(5, 10):
                            rows.append(horizon_row(sess, b, t, 0.0, 0, rew[b][t], None))

                if max_chars is not None and len(prompt) >= max_chars:
                    break
                add_line("You now play the two-armed bandit.")
                add_line(TWOARM_INSTRUCTION)
                conds, trew = rs["twoarm_cond"], rs["twoarm_rew"]
                for b in range(self.num_games_twoarm):
                    if max_chars is not None and len(prompt) >= max_chars:
                        break
                    add_line(f"Round {b + 1} (reward condition: {COND_LABEL[conds[b]]}).")
                    for t in range(10):
                        start_trial()
                        append_tok("You press [HUMAN_RESPONSE]")
                        choice = agent(prompt, choice_options=["S", "K"])
                        resp = ARM2.index(choice)
                        append_tok(f"{choice}[/HUMAN_RESPONSE]. You win {num(trew[b][t][resp])} points.")
                        rows.append(twoarm_row(sess, b, t, conds[b], trew[b][t], resp))

                if max_chars is not None and len(prompt) >= max_chars:
                    break
                add_line("You now play the restless bandit.")
                add_line(FOURARM_INSTRUCTION)
                rrew = rs["restless_rew"]
                for t in range(self.num_trials_restless):
                    start_trial()
                    append_tok("You press [HUMAN_RESPONSE]")
                    choice = agent(prompt, choice_options=["S", "D", "K", "L"])
                    resp = ARM4.index(choice)
                    append_tok(f"{choice}[/HUMAN_RESPONSE]. You gain {num(rrew[t][resp])} points.")
                    rows.append(restless_row(sess, t, rrew[t], resp))

                if max_chars is not None and len(prompt) >= max_chars:
                    break
                add_line(QUESTIONNAIRE_INSTRUCTION)
                for qname in QQ_ORDER:
                    if max_chars is not None and len(prompt) >= max_chars:
                        break
                    add_line(f"{self._qq_stem(qname)} ({SCALE_ANCHORS[qname]}).")
                    opts = [str(i) for i in range(QQ_MAX[qname] + 1)]
                    for i in range(QQ_NITEMS[qname]):
                        start_trial()
                        append_tok(f"Item {i + 1}: you respond [HUMAN_RESPONSE]")
                        choice = agent(prompt, choice_options=opts)
                        append_tok(f"{choice}[/HUMAN_RESPONSE].")
                        rows.append(qq_row(sess, qname, i, int(choice)))

            if demo["feedback"]:
                add_line(f"You give final feedback: {demo['feedback']}")
            all_rows.extend(rows)
            prompts.append(prompt)

        df = pd.DataFrame(all_rows, columns=[
            "participant_id", "trial", "response", "task_id", "session", "phase",
            "block", "reward", "info", "reward1", "reward2", "horizon",
            "forced_choice", "valid", "condition", "reward3", "reward4",
            "questionnaire", "item_index", "motiv_mem_0", "motiv_slot_0",
            "mem_aid_0", "slot_aid_0", "gender", "feedback", "age", "edu",
            "income_0", "attention1", "wm_measure",
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

    task = ExplorationBattery()
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
