# /// script
# requires-python = ">=3.10"
# dependencies = ["numpy", "pandas", "tqdm"]
# ///
"""Text simulator for exp0 of ``Hugging-Brain/badham_2017_deficits``,
format-identical to the repo's ``transcripts0.jsonl``.

``uv run simulate0.py -n 3`` smoke-tests with a uniform-random agent; or import
the class and pass your own ``agent(prompt, choice_options)``.

The generated participant text matches ``build_jsonl.py::transcribe_exp0``
exactly (same story, wording, punctuation and fixed A/B + Alpha/Beta tokens),
modulo the random draws (counterbalanced rules, stimulus order) and the
simulated agent's choices.
"""
import argparse

import numpy as np
import pandas as pd
from tqdm import tqdm

# Verbatim from build_jsonl.py.
INSTRUCTIONS = (
    "This is a category-learning task. Your goal is to learn a rule that allows you to "
    "tell whether each example belongs in the alpha or beta category: four of the shapes "
    "you will see belong in the alpha category and four belong in the beta category. "
    "On each trial a shape appears in the middle of the screen. Press A if you think it "
    "belongs in the alpha category, or press B if you think it belongs in the beta "
    "category. The words Alpha and Beta appear at the bottom corners of the screen to "
    "remind you which is which. After each response you get feedback: the same shape "
    "reappears with Correct! or Incorrect! followed by the correct answer "
    "(Answer = Alpha or Answer = Beta), and this will gradually teach you the rule. "
    "You will go through several conditions, and each one has its own new rule; you "
    "may take a break between conditions if you wish."
)

NEW_RULE = "A new rule will determine which images belong to each category. Continue."

# Feature coding of exp0.csv (fitting_analysis_rmc.R, OSF M7TCK): size 0 = Big / 1 = Small,
# colour 0 = Black / 1 = White, form 0 = Triangle / 1 = Square.
SIZE_WORD = {0: "large", 1: "small"}
COLOUR_WORD = {0: "black", 1: "white"}
FORM_WORD = {0: "triangle", 1: "square"}
CATEGORY_WORD = {0: "Alpha", 1: "Beta"}
LETTER = {0: "A", 1: "B"}


class CategoryLearning:
    """Shepard–Hovland–Jenkins category learning, Experiment/Study of Badham,
    Sanborn, & Maylor (2017), "Deficits in category learning in older adults:
    rule-based versus clustering accounts", Psychology and Aging, 32(5), 473-488.

    Design (Method section, pp. 11-14): each participant learns four SHJ
    category structures (Types I-IV) as binary two-choice classifications with
    feedback, up to 6 blocks of 16 trials per structure (96 trials, or fewer
    when two consecutive blocks are perfect; N=96 total, 48 younger / 48 older). Each block presents all 8 shapes (factorial 3
    binary features: size, colour, form) exactly twice; in blocks 1-2 the first
    half of the block holds one copy of each shape (no adjacent repeats), later
    blocks are unconstrained. The four conditions were counterbalanced across
    24 test orders, and within each condition category membership was defined
    by one of the condition's permutations (Type I: category = one dimension;
    Type II: category = equivalence of two dimensions, one irrelevant; Type
    III: rule plus exception; Type IV: an anchor corner and its three
    neighbours), with alpha/beta labels determined randomly per version.

    ASSUMPTION: the underlying source version counterbalancing (type order,
    per-type permutation, alpha/beta labels) is not recoverable from the
    shipped transcripts (build_jsonl.py fixes response 0->A/1->B and feedback
    0->Alpha/1->Beta, and narrates the four conditions in the order they were
    run, i.e. by task_id = session position). This
    simulator therefore samples, per participant, each type's rule uniformly
    from the exact structure families observed in exp0.csv (Type I: 6
    structures = 3 defining dimensions x 2 polarities; Type II: 6 = 3 relevant
    dimension pairs x 2 polarities; Type III: 24 = 3 base dimensions x 4
    exceptions x 2 polarities [one of the two non-base dimensions kept]; Type
    IV: 8 = 8 anchor corners), and runs the four types in a random order:
    task_id = position 0..3 in the session (Block = task_id + 1), condition =
    type_1..type_4 (SHJ Type I-IV). The paper says Type III was reduced
    to 3 permutations, but exp0.csv actually contains all 24 distinct Type III
    structures (each used by 4 participants); per the data-authoritative rule
    the simulator follows the data.

    Criterion (Method, p. 14): a condition ends after two consecutive perfect
    blocks of 16 trials, else after 6 blocks. exp0.csv pads the trials not
    run with imputed all-correct rows; exp0.csv, the shipped transcripts and
    this simulator contain only the trials actually run.

    ASSUMPTION: stimulus order within a block is randomized per participant
    (blocks 0-1 = two random permutations of the 8 shapes, blocks 2-5 =
    unconstrained shuffle of 8x2), matching the paper's Procedure; each shape
    appears exactly twice per block as observed in exp0.csv. The raw
    block/trial order in the source is kept: build_jsonl.py sorts by (task_id,
    block, trial), and the simulator narrates the conditions in its random
    session order.

    The DataFrame mirrors exp0.csv (columns participant_id, task_id, condition,
    block, trial, size, colour, form, response, feedback, type.block, stim.rep,
    stim.num, age_group, correct, Block) and drops rt, the
    analysis-time RMC model-output columns and the derived `centrality` label
    that a text simulator cannot produce.

    Class references the data columns: stimulus features size/colour/form are
    0/1 with semantics size 0=large/1=small, colour 0=black/1=white, form
    0=triangle/1=square; feedback is the correct category 0/1 (0 = Alpha =
    key F, 1 = Beta = key J) and correct == (response == feedback).
    """

    def __init__(self, seed=None):
        self.name = "badham_2017_deficits_exp0"
        self.num_types = 4
        self.num_blocks = 6
        self.trials_per_block = 16
        self.rng = np.random.default_rng(seed)
        # 8 stimuli in binary (size, colour, form) order; index = 4*size+2*colour+form
        self.stimuli = [(s, c, f) for s in (0, 1) for c in (0, 1) for f in (0, 1)]

    def _rule(self, task_id):
        """Return dict {(size,colour,form): feedback} for one SHJ type (0..3)."""
        dims = (0, 1, 2)
        rule = {}
        if task_id == 0:
            # Type I: one defining dimension, arbitrary polarity.
            d = int(self.rng.integers(3))
            p = int(self.rng.integers(2))
            for v in self.stimuli:
                rule[v] = int(v[d] == p)
        elif task_id == 1:
            # Type II: equivalence/XOR of two relevant dimensions, one irrelevant.
            u = int(self.rng.integers(3))
            rel = [d for d in dims if d != u]
            p = int(self.rng.integers(2))
            for v in self.stimuli:
                rule[v] = int((v[rel[0]] == v[rel[1]]) ^ p)
        elif task_id == 2:
            # Type III: rule with an exception. Base dimension d (majority value
            # p), exception e among the 4 stimuli with v[d]==p, one non-base
            # dimension k kept, compensation flips d and the other non-base j.
            d = int(self.rng.integers(3))
            k = int(self.rng.integers(2))          # kept non-base dim
            k = (k + 1 if k == d else k)           # k != d
            j = [x for x in dims if x not in (d, k)][0]
            p = int(self.rng.integers(2))
            cand = [v for v in self.stimuli if v[d] == p]
            e = list(cand[int(self.rng.integers(len(cand)))])
            comp = list(e)
            comp[d] ^= 1
            comp[j] ^= 1
            alpha = {v for v in self.stimuli if v[d] == p and v != tuple(e)}
            alpha.add(tuple(comp))
            for v in self.stimuli:
                rule[v] = int(v in alpha)
        else:
            # Type IV: an anchor corner plus its three face-neighbours.
            c = list(self.stimuli[int(self.rng.integers(8))])
            alpha = {tuple(c)}
            for i in range(3):
                n = list(c)
                n[i] ^= 1
                alpha.add(tuple(n))
            for v in self.stimuli:
                rule[v] = int(v in alpha)
        return rule

    def _block_sequence(self, block):
        rng = self.rng
        if block < 2:
            first = list(self.stimuli)
            rng.shuffle(first)
            second = list(self.stimuli)
            rng.shuffle(second)
            return first + second
        seq = list(self.stimuli) * 2
        rng.shuffle(seq)
        return seq

    def simulate(self, agent, num_simulations, max_chars=None):
        rows, prompts = [], []
        for participant in tqdm(range(num_simulations)):
            age = "younger" if participant < num_simulations / 2 else "older"
            order = self.rng.permutation(self.num_types)   # SHJ type run at each position
            rules = {t: self._rule(t) for t in range(self.num_types)}
            prompt = INSTRUCTIONS + "\n"
            done = False
            for pos, shj in enumerate(int(t) for t in order):
                if done:
                    break
                n_seen = {}
                trial = 0
                prev_perfect = False
                for block in range(self.num_blocks):
                    if max_chars is not None and len(prompt) >= max_chars:
                        done = True
                        break
                    block_perfect = True
                    for stim in self._block_sequence(block):
                        if pos != 0 and trial == 0:
                            prompt += NEW_RULE + "\n"
                        feedback = rules[shj][stim]
                        prompt += f"You see a {SIZE_WORD[stim[0]]} {COLOUR_WORD[stim[1]]} {FORM_WORD[stim[2]]}. You press [HUMAN_RESPONSE]"
                        letter = agent(prompt, choice_options=["A", "B"])
                        response = 0 if letter == "A" else 1
                        correct = 1 if response == feedback else 0
                        block_perfect = block_perfect and correct == 1
                        prompt += f"{letter}[/HUMAN_RESPONSE]. "
                        prompt += "Correct! " if correct else "Incorrect! "
                        prompt += f"The answer is {CATEGORY_WORD[feedback]}.\n"
                        n_seen[stim] = n_seen.get(stim, 0) + 1
                        rows.append({
                            "participant_id": participant, "task_id": pos,
                            "condition": f"type_{shj + 1}",
                            "block": block, "trial": trial,
                            "size": stim[0], "colour": stim[1], "form": stim[2],
                            "response": response, "feedback": feedback,
                            "type.block": block + 1,
                            "stim.rep": n_seen[stim],
                            "stim.num": 1 + 4 * stim[0] + 2 * stim[1] + stim[2],
                            "age_group": age, "correct": correct,
                            "Block": pos + 1,
                        })
                        trial += 1
                    # Criterion (Method, p. 14): two consecutive perfect blocks end the condition.
                    if block_perfect and prev_perfect:
                        break
                    prev_perfect = block_perfect
            prompts.append(prompt.strip())
        df = pd.DataFrame(rows, columns=[
            "participant_id", "task_id", "condition", "block", "trial", "size",
            "colour", "form", "response", "feedback", "type.block", "stim.rep",
            "stim.num", "age_group", "correct", "Block",
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

    task = CategoryLearning(seed=args.seed)
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